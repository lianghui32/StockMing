from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
import json
import tushare as ts
from keras import Sequential
from keras.layers import Dense, Dropout, LSTM
from sklearn.decomposition import PCA
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import os
from django.core.cache import cache
from .market import *
from datetime import datetime

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

ts.set_token('0b76ba545cf8f63fd0918a594a5a5efa36097993d4227aa9d5a344ee')
pro = ts.pro_api()

now_date = datetime.today().strftime("%Y%m%d")
'''输出参数：
ts_code: str, 股票代码  
trade_date: str, 交易日期  
open: float, 开盘价  
high: float, 最高价  
low: float, 最低价  
close: float, 收盘价  
pre_close: float, 昨收价(前复权)  
change: float, 涨跌额  
pct_chg: float, 涨跌幅 (未复权，如果是复权请用通用行情接口)  
vol: float, 成交量 (手)  
amount: float, 成交额 (千元)
'''


def calculate_rsi(data, n):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=n).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=n).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def get_ts_data(ts_code, start_date, end_date):
    print("输入的代码:", ts_code)
    ts_code = generate_stock_code(ts_code)
    if isinstance(ts_code, dict) and 'error' in ts_code:  # 检查是否返回了错误信息
        print('get_ts_data:', ts_code['error'])
        print()
        return ts_code  # 直接返回错误信息，不继续后续操作
    print("构造的代码：", ts_code)
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

        print(start_date.replace('-', ''), now_date)
        now_df = pro.daily(ts_code=ts_code, start_date=start_date.replace('-', ''),
                           end_date=now_date)
        if len(df) < 3 or len(now_df) < 3:
            raise ValueError("获取数据时发生错误：疑似为非股票代码")
        print("df.info()的信息：", df.info())
        # 数据清洗
        # 1. 处理缺失值
        print(f"行数 before dropna: {len(df)}")
        df.dropna(inplace=True)
        print(f"行数 after dropna: {len(df)}")
        # 2. 处理异常值
        df = df[df['high'] >= df['low']]
        # 3. 删除重复行
        print(f"行数 before drop_duplicates: {len(df)}")
        df.drop_duplicates(inplace=True)
        print(f"行数 after drop_duplicates: {len(df)}")

        # 收盘价涨跌幅=(收盘价-开盘价)/开盘价
        df['close-open'] = (df['close'] - df['open']) / df['open']
        # 价格波动率=(最高价-最低价)/最低价
        df['high-low'] = (df['high'] - df['low']) / df['low']
        # 股价5日平均移动值
        df['MA5'] = df['close'].rolling(5).mean()
        # 股价10日平均移动值
        df['MA10'] = df['close'].rolling(10).mean()
        # 股价30日平均移动值
        df['MA30'] = df['close'].rolling(30).mean()

        df['rsi5'] = calculate_rsi(df['close'], 5)
        df['rsi10'] = calculate_rsi(df['close'], 10)
        df['rsi30'] = calculate_rsi(df['close'], 30)
        df.fillna(value=0, inplace=True)

        # 排序数据
        df.sort_values(by='trade_date', ascending=True, inplace=True)
        now_df.sort_values(by='trade_date', ascending=True, inplace=True)
        print('数据获取成功：\n', df.tail())
        # data = df.to_dict(orient='records')
        return df, now_df
    except Exception as e:
        # 打印异常信息，或者记录到日志中
        print(f"获取数据时发生错误: {e}")
        return {'error': f"get_ts_data 错误 - {e}"}


def generate_stock_code(stock_code):
    try:
        if len(stock_code) != 6:
            raise ValueError('股票代码必须为6位数字')
        if stock_code.startswith(("50", "51", "6", "90", "7", "110", "113", "132", "204")):
            return stock_code + '.SH'  # 上海证券交易所
        elif stock_code.startswith(("00", "13", "18", "15", "16", "18", "20", "30", "39", "115", "13", "18")):
            return stock_code + '.SZ'  # 深圳证券交易所
        elif stock_code.startswith('8') or stock_code.startswith('4'):
            return stock_code + '.BJ'  # 北京证券交易所
        else:
            raise ValueError("未知股票代码，可能为其他交易所股票代码，非上交所或深交所")
    except Exception as e:
        # 处理异常并返回错误信息
        print(f"构造的代码时发生错误: {e}")
        return {'error': f"generate_stock_code 错误 - {e}"}


def lstm_predict(prices_df, look_back, test_ratio, train_epochs, features):
    # 创建训练数据集和测试数据集
    X = prices_df[features].values
    y = prices_df['close'].values
    print("原始特征数据形状:", X.shape)
    print("X:", X[:2])
    print("原始目标数据形状:", y.shape)
    print("y:", y[:5])
    # 向后移动目标数据
    y_shifted = y[1:]
    next_X = X[-look_back:]
    X = X[:-1]
    print("next_X 下一交易日的测试数据：", next_X)
    print("next_X shape:", next_X.shape)
    print("y_shifted:", y_shifted[:5])
    print("y_shifted目标数据形状:", y_shifted.shape)
    print("X数据形状:", X.shape)

    # 数据降维
    pca = PCA(n_components=5)
    X_pca = pca.fit_transform(X)
    # 使用之前拟合好的PCA对象对 next_X 进行降维
    next_X_pca = pca.transform(next_X)
    # 打印降维后的形状以确认
    print("降维后特征数据形状:", X_pca.shape)
    print("X_pca:", X_pca[:2])
    print("降维后 next_X 的形状:", next_X_pca.shape)

    # 数据归一化
    scaler = MinMaxScaler(feature_range=(0, 1))
    X_scaled = scaler.fit_transform(X_pca)
    next_X_scaled = scaler.transform(next_X_pca)
    # y_scaled = scaler.fit_transform(y.reshape(-1, 1))
    y_scaled = scaler.fit_transform(y_shifted.reshape(-1, 1))
    # # 数据归一化
    # scaler = MinMaxScaler(feature_range=(0, 1))
    # X_scaled = scaler.fit_transform(X)
    # y_scaled = scaler.fit_transform(y.reshape(-1, 1))
    print("归一化后特征数据形状:", X_scaled.shape)
    print("归一化后目标数据形状:", y_scaled.shape)
    print("X_scaled:", X_scaled[:5])
    print("y_scaled:", y_scaled[:5])

    # 将数据编入序列
    X_seq, y_seq = [], []
    count = int(len(X_scaled) - look_back)
    for i in range(count):
        X_seq.append(X_scaled[i:i + look_back])
        y_seq.append(y_scaled[i + look_back])
    X_seq, y_seq = np.array(X_seq), np.array(y_seq)
    print("序列化后特征数据形状:", X_seq.shape)
    print("序列化后目标数据形状:", y_seq.shape)
    # 序列化
    next_X_seq = [next_X_scaled]
    # 将序列化后的数据转换为模型可以处理的格式
    next_X_seq_array = np.array(next_X_seq)

    # 划分训练集和测试集
    test_count = int(test_ratio * len(X_seq))
    X_train, X_test = X_seq[:-test_count], X_seq[-test_count:]
    y_train, y_test = y_seq[:-test_count], y_seq[-test_count:]
    print("test_ratio,test_count:", test_ratio, test_count)
    print("训练集特征数据形状:", X_train.shape)
    print("测试集特征数据形状:", X_test.shape)
    print("训练集目标数据形状:", y_train.shape)
    print("测试集目标数据形状:", y_test.shape)

    # 定义 LSTM 模型
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='rmsprop', loss='mean_squared_error')

    from keras.callbacks import EarlyStopping
    # 定义 EarlyStopping 回调函数
    early_stopping = EarlyStopping(monitor='val_loss', patience=30)

    # 使用 model.fit 训练模型，并收集整个历史对象
    history = model.fit(
        X_train, y_train,
        epochs=int(train_epochs),
        batch_size=8,
        validation_data=(X_test, y_test),
        callbacks=[early_stopping],
        verbose=1
    )
    # 从历史对象中获取训练和验证损失
    train_loss_history = history.history['loss']
    val_loss_history = history.history['val_loss']

    # 预测
    train_preds = model.predict(X_train)
    test_preds = model.predict(X_test)

    # 对预测结果进行反归一化
    train_preds = scaler.inverse_transform(train_preds.reshape(-1, 1))
    test_preds = scaler.inverse_transform(test_preds.reshape(-1, 1))

    # 使用训练好的模型进行预测
    next_pred_scaled = model.predict(next_X_seq_array)

    # 对预测结果进行反归一化
    next_pred = scaler.inverse_transform(next_pred_scaled)

    # 由于只预测了一个时间点，所以取第一个元素
    next_pred_value = next_pred.flatten()[0]

    # 打印预测结果
    print("预测的下一交易日收盘价:", next_pred_value)

    # 计算mse分数
    train_mse = mean_squared_error(prices_df['close'][look_back:look_back + len(train_preds)], train_preds)
    test_mse = mean_squared_error(prices_df['close'][-len(test_preds):], test_preds)
    print(f'Train Score: {train_mse}')
    print(f'Test Score: {test_mse}')

    # 计算训练集和测试集的 MAE
    train_mae = mean_absolute_error(prices_df['close'][look_back:look_back + len(train_preds)], train_preds)
    test_mae = mean_absolute_error(prices_df['close'][-len(test_preds):], test_preds)
    print(f'Train MAE: {train_mae}')
    print(f'Test MAE: {test_mae}')
    print("train_loss_history:", train_loss_history)
    print('val_loss_history', val_loss_history)

    # 将预测的测试集结果转换为列表
    test_preds_list = test_preds.flatten().tolist()

    # 将 next_pred_value 添加到测试集预测结果的列表中
    test_preds_list.append(float(next_pred_value))

    # 为 ECharts 准备预测图数据
    prediction_data = {
        'dates_train': prices_df['trade_date'][look_back:look_back + len(train_preds)].tolist(),
        'dates_test': prices_df['trade_date'][-len(test_preds):].tolist() + ['下一交易日'],
        'actual_train': prices_df['close'][look_back:look_back + len(train_preds)].tolist(),
        'actual_test': prices_df['close'][-len(test_preds):].tolist(),
        'predicted_train': train_preds.flatten().tolist(),
        'predicted_test': test_preds_list
    }

    # 为 ECharts 准备数据
    chart_data = {
        'prediction': prediction_data,
        'train_mse': float(train_mse),
        'test_mse': float(test_mse),
        'train_mae': float(train_mae),
        'test_mae': float(test_mae),
        'loss_values': {
            'train_loss_history': train_loss_history,
            'val_loss_history': val_loss_history
        }
    }

    # 将数据转换为 JSON 格式
    lstm_data = json.dumps(chart_data)
    # 返回 JSON 格式的数据
    return lstm_data


def random_forest_predict(prices_df, features, target, test_ratio=0.2, n_estimators=100):
    # 将数据拆分为特征和目标
    X = prices_df[features].values
    y = prices_df[target].values
    print("原始特征数据形状:", X.shape)
    print("X:", X[:2])
    print("原始目标数据形状:", y.shape)
    print("y:", y[:5])
    # 向后移动目标数据
    y_shifted = y[1:]
    next_X = X[-1]
    X = X[:-1]
    print("下一交易日的测试数据：", next_X)
    print("y_shifted:", y_shifted[:5])
    print("y_shifted目标数据形状:", y_shifted.shape)
    print("X数据形状:", X.shape)
    # 将数据分成训练集和测试集
    test_count = int(test_ratio * len(X))
    train_X, train_y = X[:-test_count], y_shifted[:-test_count]
    test_X, test_y = X[-test_count:], y_shifted[-test_count:]

    # # 将数据分成训练集和测试集
    # test_count = int(test_ratio * len(X))
    # print("test_ratio,test_count:", test_ratio, test_count)
    # train_X, train_y = X[:-test_count], y[:-test_count]
    # test_X, test_y = X[-test_count:], y[-test_count:]
    print("test_ratio,test_count:", test_ratio, test_count)
    print("训练集特征数据形状:", train_X.shape)
    print("测试集特征数据形状:", test_X.shape)
    print("训练集目标数据形状:", train_y.shape)
    print("测试集目标数据形状:", test_y.shape)

    # 创建并训练随机森林模型
    rf_model = RandomForestRegressor(n_estimators=n_estimators, max_depth=10)
    rf_model.fit(train_X, train_y)

    # 进行预测
    train_predict = rf_model.predict(train_X)
    test_predict = rf_model.predict(test_X)
    # 预测下一个交易日
    next_X = next_X.reshape(1, -1)
    next_predict = rf_model.predict(next_X)

    # 打印预测结果
    print("训练集预测结果形状:", train_predict.shape)
    print("测试集预测结果形状:", test_predict.shape)
    print("实际测试值：", y[-5:])
    print("实际测试值：", y_shifted[-5:])
    print("预测测试值：", test_predict[-5:])
    print("下一交易日价格：", next_predict)
    # 计算性能指标
    train_mse = mean_squared_error(train_y, train_predict)
    test_mse = mean_squared_error(test_y, test_predict)
    # 用模型自带的score函数计算整体的预测准确度
    rf_R2 = rf_model.score(test_X, test_y)
    # 打印性能指标
    print("训练集MSE:", train_mse)
    print("测试集MSE:", test_mse)
    print("测试集R方分数:", rf_R2)
    features = prices_df[features].columns
    importances = rf_model.feature_importances_
    a = pd.DataFrame()
    a['特征'] = features
    a['特征重要性'] = importances
    # 按照特征重要性从大到小排序
    a = a.sort_values(by='特征重要性', ascending=False)
    print(a)

    evaluation_metrics = {
        "train_mse": train_mse,
        "test_mse": test_mse,
        " R² 分数": rf_R2
    }

    data = {
        "train_data": {
            "x": prices_df['trade_date'][:-test_count].tolist(),
            "y_actual": train_y.tolist(),
            "y_predicted": train_predict.tolist()
        },
        "test_data": {
            "x": prices_df['trade_date'][-test_count:].tolist() + ["下一交易日"],
            "y_actual": test_y.tolist(),
            "y_predicted": test_predict.tolist() + [next_predict[0]]
        },
        "evaluation_metrics": evaluation_metrics,
        "feature_importance": a.to_dict(orient='records')
    }
    # 返回预测和性能指标
    rf_data = json.dumps(data)
    return rf_data


def get_cached_data(ts_code, start_date, end_date):
    print("检测缓存数据")
    cache_key = f"ts_data_{ts_code}_{start_date}_{end_date}"
    now_cache_key = f"ts_data_{ts_code}_{start_date}_{now_date}"
    data = cache.get(cache_key)
    now_df = cache.get(now_cache_key)
    if data is None or now_df is None:
        print("没有本地缓存数据，向Tushare API获取新数据")
        try:
            data, now_df = get_ts_data(ts_code, start_date.replace('-', ''), end_date.replace('-', ''))
            if isinstance(data, dict) and 'error' in data:  # 检查是否返回了错误信息
                print("get_cached_data:", data['error'])
                return data  # 直接返回错误信息
            print("将数据存储在本地缓存...")
            cache.set(cache_key, data, timeout=1800)
            cache.set(now_cache_key, now_df, timeout=1800)
            return data, now_df
        except Exception as e:
            # 处理从 get_ts_data 调用期间发生的异常，并返回错误信息
            print(f"获取缓存数据时发生错误: {e}")
            return {'error': f"get_cached_data - 获取数据时发生错误: {e}"}

    else:
        print("有缓存数据，使用本地缓存数据")
        return data, now_df


@csrf_exempt
def lstm_pre(request):
    if request.method == 'POST':
        ts_code = request.POST.get("ts_code")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        st_name = request.POST.get("name")
        print(f"ts_code:{ts_code}, start_date:{start_date}, end_date:{end_date}, st_name:{st_name}")
        look_back = request.POST.get("look_back")
        test_ratio = request.POST.get("test_ratio")
        train_epochs = request.POST.get("train_epochs")
        print(f"look_back:{look_back}, test_ratio:{test_ratio}, train_epochs:{train_epochs}")
        if st_name == "":
            if not ts_code.isdigit():
                print("非纯数字，id转为name用于搜索名称代码")
                st_name = ts_code
                ts_code = get_csv_code(st_name)
        else:
            ts_code = get_csv_code(st_name)
        print(f"ts_code:{ts_code}, st_name:{st_name}")
        if ts_code and start_date and end_date:
            data, now_df = get_cached_data(ts_code, start_date, end_date)
            print(data.head(2))
            if isinstance(data, dict) and 'error' in data:
                error = data['error']
                print('lstm_pre:', error)
                return JsonResponse({'error': error})
            try:
                print("lstm预测...")
                print("表头：", data.columns)
                print("数据：\n", data.head(2))

                # features = ['open', 'high', 'low', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']
                # features = ['open', 'high', 'low', 'pre_close', 'close-open', 'pct_chg', 'vol', 'amount', 'high-low',
                #             'change', 'trade_date',
                #             'close']
                features = ['trade_date', 'open', 'high', 'low', 'close', 'pre_close',
                            'change', 'pct_chg', 'vol', 'amount', 'close-open', 'high-low', 'MA5', 'rsi5']
                test_ratio = float(test_ratio)
                look_back = int(look_back)
                train_epochs = int(train_epochs)
                lstm_data = lstm_predict(data, look_back, test_ratio, train_epochs, features)
                # print(lstm_data)
                # 将DataFrame转换为JSON格式

                k_data = now_df.to_json(orient='records')

                data_json = {
                    'k_data': k_data,
                    'lstm_data': lstm_data,
                }
                print(type(data_json))
                # data_json = {'a': 'a'}
                return JsonResponse(data_json, safe=False)
            except Exception as e:
                # 处理异常并返回错误信息
                return JsonResponse({'error': 'lstm_pre预测过程报错'})
        else:
            return JsonResponse({'error': '请输入有效的股票代码和时间'})
    else:
        return render(request, "prediction.html")


@csrf_exempt
def rf_pre(request):
    if request.method == 'POST':
        ts_code = request.POST.get("ts_code")
        start_date = request.POST.get("start_date")
        end_date = request.POST.get("end_date")
        st_name = request.POST.get("name")
        print(f"ts_code:{ts_code}, start_date:{start_date}, end_date:{end_date}, st_name:{st_name}")
        test_ratio = request.POST.get("test_ratio")
        n_estimators = int(request.POST.get("n_estimators"))
        print(f"test_ratio:{test_ratio}, n_estimators:{n_estimators}")
        if st_name == "":
            if not ts_code.isdigit():
                print("非纯数字，id转为name用于搜索名称代码")
                st_name = ts_code
                ts_code = get_csv_code(st_name)
        else:
            ts_code = get_csv_code(st_name)
        print(f"ts_code:{ts_code}, st_name:{st_name}")
        if ts_code and start_date and end_date:
            data = get_cached_data(ts_code, start_date, end_date)
            if isinstance(data, dict) and 'error' in data:
                error = data['error']
                print('rf_pre:', error)
                return JsonResponse({'error': error})
            try:
                print("随机森林预测...")
                features = ['open', 'high', 'low', 'pre_close', 'close-open', 'pct_chg', 'vol', 'amount', 'high-low',
                            'change', 'trade_date',
                            'close']
                target = 'close'
                test_ratio = float(test_ratio)
                rf_data = random_forest_predict(data, features, target, test_ratio, n_estimators)
                print(rf_data)
                data_json = {
                    'rf_data': rf_data
                }
                print(type(data_json))
                # data_json = {'a': 'a'}
                return JsonResponse(data_json, safe=False)
            except Exception as e:
                # 处理异常并返回错误信息
                return JsonResponse({'error': 'rf_pre预测过程报错'})
        else:
            return JsonResponse({'error': '请输入有效的股票代码和时间'})
    else:
        return render(request, "prediction.html")


def show_pre(request):
    return render(request, "prediction.html")

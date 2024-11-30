import json
import requests
from django.contrib.staticfiles import finders
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pandas as pd

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    "Cookie": "qgqp_b_id=e778b242b97b124532fe2b3981c06dcc; emshistory=%5B%22000001%22%5D; websitepoptg_api_time=1711887019927; st_si=29926566787139; st_asi=delete; HAList=ty-1-000001-%u4E0A%u8BC1%u6307%u6570%2Cty-0-000680-%u5C71%u63A8%u80A1%u4EFD%2Cty-0-000001-%u5E73%u5B89%u94F6%u884C%2Cty-0-300420-%u4E94%u6D0B%u505C%u8F66%2Cty-0-000860-%u987A%u946B%u519C%u4E1A%2Cty-0-399001-%u6DF1%u8BC1%u6210%u6307; st_pvi=52155918792792; st_sp=2023-03-28%2010%3A06%3A27; st_inirUrl=https%3A%2F%2Fwww.eastmoney.com%2F; st_sn=64; st_psi=20240402001639291-113200302671-3888278012",
    "Host": None,
    "Referer": None,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
}


# 定义半角转全角的函数，跳过中文字符
def half_to_full(ch):
    if 0x0020 <= ord(ch) <= 0x007E:  # 半角字符的范围从0x0020到0x007E
        if ch.isdigit() or ch.isalpha():  # 检查是否是半角数字或英文字符
            # 转换为全角字符
            return chr(ord(ch) + 0xfee0)
        else:
            # 对于半角空格和标点符号等，保持不变
            return ch
    elif 0x4E00 <= ord(ch) <= 0x9FA5:  # 保留中文字符不变
        return ch
    else:
        # 对于其他字符，保持不变
        return ch


# 定义一个函数，用于对DataFrame的列进行半角转全角的转换
def convert_column_half_to_full(column_series):
    # 使用列表推导式和half_to_full函数进行转换
    return ''.join(half_to_full(ch) for ch in column_series)


def get_csv_code(st_name):
    # 使用staticfiles的finders来获取文件的绝对路径
    csv_file_path = finders.find('stock_code_name.csv')

    if csv_file_path is None:
        raise FileNotFoundError("CSV file not found")

    # 读取CSV文件
    stock_info_a_code_name_df = pd.read_csv(csv_file_path, dtype={'code': str})
    # 将全角字符转换为全角字符
    stock_info_a_code_name_df['name'] = stock_info_a_code_name_df['name'].str.replace(" ", "").apply(
        convert_column_half_to_full)
    st_name = convert_column_half_to_full(st_name)

    # print(stock_info_a_code_name_df['name'])
    # 将DataFrame转换为字典
    stock_dict = dict(zip(stock_info_a_code_name_df['name'], stock_info_a_code_name_df['code']))
    # print("json:stock_dict\n", stock_dict)
    try:
        if st_name in stock_dict:
            return stock_dict[st_name]
        else:
            raise ValueError("没有搜索到相应股票名称或代码")
    except Exception as e:
        # 处理异常并返回错误信息
        print(f"没有搜索到相应股票名称或代码: {e}")
        return {'error': f"get_csv_code 错误 - {e}"}


def get_security_type(security_code: str):
    """
    根据股票代码判断所属证券市场
    """
    just_code = security_code.replace('.', '').replace("SH", '').replace("SZ", '')
    try:
        if len(just_code) != 6:
            raise ValueError('股票代码必须为6位数字')
        elif security_code.startswith(
                ("50", "51", "6", "90", "7", "110", "113", "132", "204")
        ):
            return "SH"
        elif security_code.startswith(
                ("00", "13", "18", "15", "16", "18", "20", "30", "39", "115", "13", "18")
        ):
            return "SZ"
        elif security_code.startswith('8') or security_code.startswith('4'):
            return 'BJ'  # 北京证券交易所
        else:
            raise ValueError("未知股票代码，可能为其他交易所股票代码，非上交所或深交所")
    except Exception as e:
        # 处理异常并返回错误信息
        print(f"判断代码所属证券市场时发生错误: {e}")
        return {'error': f"get_security_type 错误 - {e}"}


def get_stock_kline_time(secid, st_name, market_type):
    if secid == "":
        print("id为空，使用名称查找id")
        secid = get_csv_code(st_name)
        if isinstance(secid, dict) and 'error' in secid:  # 检查是否返回了错误信息
            print("get_cached_data:", secid['error'])
            return secid  # 直接返回错误信息
        print(secid)
        market_type = None

    security_type = None
    if secid.endswith(("SH")):
        secid = secid[0:6]
        market_type = int(1)
    elif secid.endswith(("SZ")):
        secid = secid[0:6]
        market_type = int(0)
    else:
        if not market_type:
            security_type = get_security_type(secid)
            print("security_type:", security_type)
            if isinstance(security_type, dict) and 'error' in security_type:  # 检查是否返回了错误信息
                print("get_cached_data:", security_type['error'])
                return security_type  # 直接返回错误信息
            elif security_type == 'SH':
                market_type = int(1)
            elif security_type == 'SZ':
                market_type = int(0)
            elif security_type == 'BJ':
                market_type = int(0)
            else:
                pass
    print('secid:', secid)
    print('market_type:', market_type)

    url = f'https://push2his.eastmoney.com/api/qt/stock/trends2/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58&ut=fa5fd1943c7b386f172d6893dbfba10b&iscr=0&ndays=1&secid={market_type}.{secid}&_=1711960032052'
    # url='https://push2his.eastmoney.com/api/qt/stock/trends2/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58&ut=fa5fd1943c7b386f172d6893dbfba10b&iscr=0&ndays=1&secid=1.000001&_=1711960032052'
    #     print(url)
    try:
        resp = requests.get(url, headers)
        resp.encoding = 'utf8'
        print(resp.status_code)
        # resp_data = resp.json()['data']
        print("market:", resp.json()['data']['market'])
        st_code = resp.json()['data']['code']
        if security_type is None:
            if resp.json()['data']['market'] == 1:
                st_code = st_code + ".SH"
            elif resp.json()['data']['market'] == 0:
                st_code = st_code + ".SZ"
        else:
            if security_type == 'SZ':
                st_code = st_code + ".SZ"
            elif security_type == 'BJ':
                st_code = st_code + ".BJ"
            else:
                st_code = st_code + ".SH"

        st_name = resp.json()['data']['name']
        resp_trends = resp.json()['data']['trends']
    except Exception as e:
        # 处理异常并返回错误信息
        print(f"获取接口数据或处理时发生错误: {e}")
        return {'error': f"get_stock_kline_time 错误 - {e}"}

    xDatas = []  # 时间戳列表
    sDatas = []  # 开盘、收盘、最低、最高值列表

    for data_string in resp_trends:
        parts = data_string.split(',')
        timestamp = parts[0]  # 时间戳
        open_value = float(parts[1])  # 开盘值
        close_value = float(parts[2])  # 收盘值
        low_value = float(parts[3])  # 最低值
        high_value = float(parts[4])  # 最高值

        xDatas.append(timestamp)
        sDatas.append([open_value, close_value, low_value, high_value])
    # print(xDatas)
    # print(sDatas)

    return {
        'st_code': st_code,
        'st_name': st_name,
        'xDatas': xDatas,
        'sDatas': sDatas
    }


@csrf_exempt
def Today_data(request):
    if request.method == 'POST':
        # received_data = json.loads(request.body.decode('utf-8'))
        # id_value = received_data.get('id')
        # st_name = received_data.get('name')
        # market_type = received_data.get('market_type')
        # print(f"id:{id_value}, name:{st_name}, market_type:{market_type}")
        # if id_value is None:
        #     id_value = '000001'  # 设置默认值为 '000001',上证指数
        #     market_type = '1'
        # print(id_value)
        # if st_name == "":
        #     if not id_value.isdigit():
        #         print("非纯数字，id转为name用于搜索名称代码")
        #         st_name = id_value
        #         id_value = ""
        # print(f"id:{id_value}, name:{st_name}, market_type:{market_type}")
        # # 获取最近交易日分时K线数据
        # # market_type = None
        # dataset = get_stock_kline_time(secid=id_value, st_name=st_name, market_type=market_type)
        # if isinstance(dataset, dict) and 'error' in dataset:  # 检查是否返回了错误信息
        #     print("get_cached_data:", dataset['error'])
        #     error = dataset['error']
        #     return JsonResponse({'error': error})
        # # print(dataset)
        # # json_data = json.dumps(dataset)
        # return JsonResponse(dataset, safe=False)
        return JsonResponse({'error': '功能升级中，暂停服务'})
    else:
        get_value = request.GET.get('id')
        print("GET", get_value)  # 打印ID值
        return JsonResponse({'error': 'Invalid request method'})


def market_tb(request):
    url = "https://push2.eastmoney.com/api/qt/clist/get?&fid=f184&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&fields=f2,f3,f12,f13,f14,f62,f184,f225,f165,f263,f109,f175,f264,f160,f100,f124,f265,f1&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2"

    resp = requests.get(url, headers)
    print(resp)
    resp.encoding = 'utf8'
    print(resp.status_code)
    data = resp.json()['data']['diff']
    print('data:\n', data)
    paginator = Paginator(data, 10)  # 每页显示10条数据
    page = request.GET.get('page')

    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    print(data)
    return render(request, 'market.html', {'data': data})


def get_stock_name(request):
    # # 使用staticfiles的finders来获取文件的绝对路径
    # csv_file_path = finders.find('stock_code_name.csv')
    #
    # if csv_file_path is None:
    #     raise FileNotFoundError("CSV file not found")
    #
    # # 读取CSV文件
    # stock_info_a_code_name_df = pd.read_csv(csv_file_path)
    #
    # # 打印数据框的内容
    # # print(stock_info_a_code_name_df['name'])
    # # 获取股票名称列表
    # stock_names = stock_info_a_code_name_df['name'].str.replace(" ", "").tolist()
    # # print(stock_names)
    # return JsonResponse({"stock_names": stock_names}, safe=False)
    return JsonResponse({'error': '功能升级中，暂停服务'})

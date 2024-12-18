import csv
import json

import pandas as pd
from django.contrib.staticfiles import finders
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render


def search_stocks(request):
    # 使用staticfiles的finders来获取文件的绝对路径
    csv_file_path = finders.find('stocks.csv')

    if csv_file_path is None:
        raise FileNotFoundError("CSV file not found")

    # 读取CSV文件
    stock_info_a_code_name_df = pd.read_csv(csv_file_path, dtype={'code': str})
    print(stock_info_a_code_name_df)
    return JsonResponse({'status': 'ok', 'data': stock_info_a_code_name_df.to_dict(orient='records')})


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
    csv_file_path = finders.find('stocks.csv')

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

import akshare as ak

def get_stock_list():
    try:
        # 获取A股所有股票的代码和名称
        stock_info = ak.stock_info_a_code_name()
        
        # 保存到csv文件
        stock_info.to_csv('../static/stocks.csv', encoding='utf-8-sig', index=False)
        
        print('股票列表已保存到文件：股票列表_akshare.csv')
        return stock_info
        
    except Exception as e:
        print(f'发生错误：{str(e)}')
        return None

if __name__ == '__main__':
    stock_list = get_stock_list()
    if stock_list is not None:
        print(f'共获取到 {len(stock_list)} 只股票')
        print('\n前5只股票示例：')
        print(stock_list.head())
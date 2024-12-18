let stockData = [];

$(document).ready(function() {
    // 使用 AJAX 请求获取股票数据
    $.ajax({
        url: '/search_stocks/', // 请求的 URL
        type: 'GET', // 请求类型为 GET
        success: function (data) {
            stockData = data.data; // 将返回的数据存储到 stockData 变量中
            console.log(stockData); // 打印数据到控制台
        },
    });

//    // 当搜索框被点击时，显示所有股票信息
//    $('#stockSearch').on('click', function() {
//        displayResults(stockData);
//    });

    // 当搜索框内容发生变化时，根据输入值过滤股票信息
    $('#stockSearch').on('input', function() {
        let searchValue = $(this).val().toLowerCase(); // 获取输入值并转换为小写
        if (searchValue === '') {
            $('#searchResults').hide(); // 如果输入为空，隐藏搜索结果
            return;
        }

        // 过滤 stockData 中包含输入值的股票信息
        let filteredData = stockData.filter(stock =>
            stock.code.toLowerCase().includes(searchValue) || // 检查股票代码是否包含输入值
            stock.name.toLowerCase().includes(searchValue)   // 检查股票名称是否包含输入值
        );

        displayResults(filteredData); // 显示过滤后的结果
    });

    // 处理搜索结果项上的点击事件。
    $('#searchResults').on('click', '.search-item', function() {
        let stockName = $(this).text().split(' - ')[1]; // 从点击的项目中提取股票名称
        $('#stockSearch').val(stockName); // 将搜索输入值设置为所选的股票名称
        $('#searchResults').hide(); // 选择后隐藏搜索结果。
    });


    // 显示搜索结果的函数
    function displayResults(data) {
        let resultsHtml = ''; // 初始化结果 HTML 字符串
        data.forEach(stock => {
            // 遍历数据，将每一条股票信息添加到结果 HTML 字符串中
            resultsHtml += `<div class="search-item">${stock.code} - ${stock.name}</div>`;
        });

        $('#searchResults').html(resultsHtml).show(); // 将结果 HTML 字符串插入到搜索结果容器中并显示
    }

});

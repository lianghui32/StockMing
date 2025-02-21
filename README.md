# StockMing

gitee仓库：[https://gitee.com/lianghui2333/stock-ming](https://gitee.com/lianghui2333/stock-ming)
github仓库：[https://github.com/lianghui32/StockMing](https://github.com/lianghui32/StockMing)

StockMing 是一个简易的股票预测系统，其功能可能未能满足所有人的期望。🙏我对此表示歉意，并期待未来能够提供更完善的服务。已线上部署的网站示例：[登录](http://175.178.120.28:8001/login/) 



**另一个之前跟别人买的基于flask+lstm的系统仓库地址**：[lh/flask_stockv2](https://gitee.com/lianghui2333/flask_stockv2)



目前，系统在资源方面依赖于线上资源，例如前端组件，使用了 Bootstrap、jQuery 和 ECharts 等库，并通过 CDN 获取这些资源。虽然在本地的 `/static/` 目录下也提供了这些资源，但在云服务器上部署时（当 `debug` 设置为 `false`），可能会遇到跨域问题，导致资源路径无法找到。然而，当 `debug` 设置为 `true` 时，这个问题就不会出现。因此，我们选择了使用 CDN 来简化部署过程。

此外，系统获取股票数据依赖于 Tushare 和东方财富网，这也需要网络连接。当前的前端设计相对简单，且每次进行预测时都需要重新训练模型，这无疑会消耗更多的资源和时间。

我们计划在未来对系统进行改进，包括使用 layui 重写前端界面，以提供更好的用户体验。同时，我们也打算将模型训练过程单独提出，并在训练完成后保存模型。这样，在需要进行预测时，可以直接调用已保存的模型，而无需每次都重新训练，从而提高效率。

如果对你有帮助，可以来我的B站工房支持我[希望不会挂科的个人空间-希望不会挂科个人主页-哔哩哔哩视频 (bilibili.com)](https://space.bilibili.com/28607239) 只需要10块❤️。

## 介绍

StockMing 是一个基于 Django 框架开发的股票预测系统，旨在为用户提供一个直观、易用的界面来管理账户信息、获取股票数据、进行数据预处理、训练预测模型，并实时查看市场行情。它只是一个简易的系统，功能可能远远没有达到各位的预期要求。

### 项目描述：

- **账户信息管理模块**：利用 Django 框架内建的 User 模型，实现了用户注册、登录、登出等功能，确保用户信息的安全和便捷管理。
- **数据获取与预处理模块**：通过 Tushare 网站获取股票历史数据，并进行数据清洗、特征工程等预处理步骤，为模型训练准备高质量的数据。
- **股票价格预测模块**：采用<mark>随机森林（前端部分注释了，可以取消注释来启用）</mark>和 LSTM（长短期记忆网络）算法对股票价格进行预测分析，为用户提供可能的价格走势。
- **实时行情模块**：实时展示市场行情，包括股票价格、交易量等关键信息，帮助用户把握市场动态。

## 软件架构

StockMing 的软件架构包括以下几个主要组件：

- **前端界面**：使用 HTML/CSS/JavaScript 构建的用户界面，提供直观的操作体验。
- **后端服务**：基于 Django 框架，处理业务逻辑、数据库操作和 API 接口。
- **数据库**：使用 SQLite 作为开发阶段的数据库，存储用户信息、股票数据和预测结果。
- **数据预处理和模型训练**：Python 脚本负责数据清洗、特征提取和模型训练。
- **预测算法**：集成随机森林和 LSTM 算法，对股票价格进行预测。

## 安装教程

### 本地环境

1. **创建Python虚拟环境并启用**：
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # 在Windows系统使用 venv\Scripts\activate
   ```

2. **安装依赖库**：
   
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple # 如果下载慢的话可以使用国内镜像源
   ```

3. **配置数据库**：
   
   - 确保 `db.sqlite3` 文件在项目根目录下。
   
   - 运行数据库迁移命令：
     
     ```bash
     python manage.py migrate
     ```

4. **创建管理员账号**（登录admin后台）：
   
   ```bash
   python manage.py createsuperuser
   ```

5. **运行开发服务器**：
   
   ```bash
   python manage.py runserver
   ```

### Docker环境

1. **构建 Docker 镜像**（如果需要）：
   
   ```bash
   docker build -t my-django-app .
   ```

2. **运行 Docker 容器**：
   
   ```bash
   docker run -p 8001:8000 -v "$(pwd)":/app -v "$(pwd)/db.sqlite3":/app/db.sqlite3 --name stock_system my-django-app
   ```
   
   - 将容器的 8000 端口映射到主机的 8001 端口。
   - 将当前目录挂载到容器的 `/app` 目录，以便进行文件操作。
   - 使用 `db.sqlite3` 文件作为数据库。

## 使用说明

1. **访问应用**：
   
   - 在浏览器中输入 `http://localhost:8001` 访问 StockMing 应用。

2. **注册和登录**：
   
   - 使用注册功能创建新用户，或使用现有账户登录。

3. **获取和预处理数据**：
   
   - 通过数据获取模块从 Tushare 获取数据，并进行必要的预处理。

4. **训练和预测**：
   
   - 使用随机森林或 LSTM 模型对股票价格进行训练和预测。

5. **查看实时行情**：
   
   - 在实时行情模块查看当前市场的股票价格和交易量。

请结合上述文档内容并根据您的实际情况使用。希望这些信息对您有所帮助！

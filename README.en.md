# StockMing

Gitee repository: [https://gitee.com/lianghui2333/stock-ming](https://gitee.com/lianghui2333/stock-ming)  
GitHub repository: [https://github.com/lianghui32/StockMing](https://github.com/lianghui32/StockMing)  

StockMing is a simple stock prediction system. Its functionality may not meet everyone's expectations.🙏 I apologize for this and look forward to providing more comprehensive services in the future. An example of a deployed website is available at: [Demo Website](http://175.178.120.28:8001/login/)

**Another repository for a previously purchased system based on Flask + LSTM**: [lh/flask_stockv2](https://gitee.com/lianghui2333/flask_stockv2)

Currently, the system relies on online resources, such as front-end components, using libraries like Bootstrap, jQuery, and ECharts, which are obtained via CDN.

Additionally, the system depends on Tushare and East Money for stock data, which requires an internet connection. The current front-end design is relatively simple, and the need to retrain the model every time a prediction is made consumes more resources and time.

If this is helpful to you, please give it a Star❤️.

## Introduction

StockMing is a stock prediction system developed using the Django framework. It aims to provide users with an intuitive and user-friendly interface to manage account information, obtain stock data, preprocess data, train prediction models, and view real-time market trends. It is a simple system, and its functionality may fall short of your expectations.

### Project Description:

* **Account Information Management Module**: Utilizes the built-in User model of the Django framework to implement user registration, login, and logout functionalities, ensuring the security and convenient management of user information.
* **Data Acquisition and Preprocessing Module**: Obtains historical stock data from Tushare and performs data cleaning and feature engineering to prepare high-quality data for model training.
* **Stock Price Prediction Module**: Uses Random Forest and LSTM (Long Short-Term Memory) algorithms to predict stock prices and provide potential price trends.
* **Real-Time Market Trends Module**: Displays real-time market trends, including key information such as stock prices and trading volumes, to help users grasp market dynamics.

## Software Architecture

The software architecture of StockMing includes the following main components:

* **Front-End Interface**: A user interface built with HTML/CSS/JavaScript that provides an intuitive user experience.
* **Back-End Service**: Based on the Django framework, it handles business logic, database operations, and API interfaces.
* **Database**: SQLite is used as the database during the development phase to store user information, stock data, and prediction results.
* **Data Preprocessing and Model Training**: Python scripts are responsible for data cleaning, feature extraction, and model training.
* **Prediction Algorithms**: Integrates Random Forest and LSTM algorithms for stock price prediction.

## Installation Guide

### Local Environment

1. **Create and activate a Python virtual environment**:
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows, use venv\Scripts\activate
   ```

2. **Install dependencies**:
   
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple  # Use a domestic mirror source if the download is slow
   ```

3. **Configure the database**:
   
   * Ensure that the `db.sqlite3` file is in the project root directory.
   
   * Run the database migration command:
     
     ```bash
     python manage.py migrate
     ```

4. **Create a superuser account** (for admin backend access):
   
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**:
   
   ```bash
   python manage.py runserver
   ```

### Docker Environment

1. **Build a Docker image** (if needed):
   
   ```bash
   docker build -t my-django-app .
   ```

2. **Run the Docker container**:
   
   ```bash
   docker run -p 8001:8000 -v "$(pwd)":/app -v "$(pwd)/db.sqlite3":/app/db.sqlite3 --name stock_system my-django-app
   ```
   
   * Maps the container's port 8000 to the host's port 8001.
   * Mounts the current directory to the container's `/app` directory for file operations.
   * Uses the `db.sqlite3` file as the database.

## Usage Instructions

1. **Access the application**:
   
   * Enter `http://localhost:8001` in your browser to access the StockMing application.

2. **Register and log in**:
   
   * Create a new user using the registration feature or log in with an existing account.

3. **Acquire and preprocess data**:
   
   * Obtain data from Tushare through the data acquisition module and perform necessary preprocessing.

4. **Train and predict**:
   
   * Use Random Forest or LSTM models to train and predict stock prices.

5. **View real-time market trends**:
   
   * Check the current market stock prices and trading volumes in the real-time market trends module.

Please refer to the above documentation and use it according to your actual situation. I hope this information is helpful to you!

# 使用官方 Python 3.11 镜像作为基础镜像
FROM python:3.11-slim

# 设置容器内的工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到容器内工作目录
COPY . /app

# 使用 pip 安装 requirements.txt 中的依赖
RUN pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/


# 让 8000 端口可供外部访问
EXPOSE 8000

# 定义环境变量，这可以是您的数据库配置等
# ENV NAME World
RUN python manage.py collectstatic --noinput
# 运行 Django 的 runserver 命令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

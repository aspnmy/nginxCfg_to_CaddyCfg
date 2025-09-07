# 构建阶段
FROM python:3.13-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# 运行阶段
FROM python:3.13-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .

# 创建uploads目录
RUN mkdir -p uploads

# 设置环境变量
ENV PATH=/root/.local/bin:$PATH
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 使用gunicorn作为WSGI服务器（推荐生产环境使用）
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

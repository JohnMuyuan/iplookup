FROM python:3.10-slim

WORKDIR /app

# 安装系统级 whois 依赖，这是解析所有新顶级域名的灵魂
RUN apt-get update && apt-get install -y whois && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
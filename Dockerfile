# Python image
FROM python:3.13-slim

# Thư mục làm việc trong container
WORKDIR /app

# Copy requirements trước để tận dụng cache
COPY requirements.txt .

# Cài thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code
COPY . .

# Flask chạy ở cổng 5000
EXPOSE 5000

# Chạy ứng dụng
CMD ["python", "app.py"]
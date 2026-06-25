FROM python:3.10-alpine

WORKDIR /app

# Copy seluruh file program ke dalam container
COPY . .
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Expose port sesuai yang digunakan aplikasi Anda
EXPOSE 3000

# Jalankan langsung file python-nya
ENTRYPOINT ["python", "server.py"]
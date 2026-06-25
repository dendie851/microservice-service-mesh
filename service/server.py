from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import sys
import json
import datetime
import jwt # <--- Menggunakan pustaka PyJWT

# Mengambil nama service dasar dari argumen
SERVICE_NAME = sys.argv[1] if len(sys.argv) > 1 else "Generic Service"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 3000

# Kredensial JWT yang WAJIB SAMA dengan yang tertulis di kong.yml
JWT_SECRET = "kunciRahasiaSuperAman123"
JWT_ISSUER = "iss-kampus-kita"

# Template HTML Dinamis untuk Order dan Payment
def generate_html(current_service, current_path):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{current_service} - Active</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 40px; background: #f5f5f5; }}
        h1 {{ color: #1a1a1a; border-bottom: 3px solid #2ecc71; padding-bottom: 10px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin: 15px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .endpoint {{ background: #2c3e50; color: white; padding: 5px 10px; border-radius: 4px; font-family: monospace; font-size: 16px; }}
        .status {{ color: #27ae60; font-weight: bold; font-size: 18px; }}
        .info-block {{ background: #f9f9f9; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 5px solid #2ecc71; }}
        .port {{ background: #7f8c8d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>{current_service} Dashboard</h1>
    <div class="card">
        <h2>Service Status: <span class="status">ONLINE</span></h2>
        <div class="info-block">
            <p>Sistem mendeteksi request masuk melalui gateway pada jalur:</p>
            <p><span class="endpoint">GET {current_path}</span></p>
        </div>
        <p>Kontainer aktif melayani pada internal <span class="port">port {PORT}</span></p>
    </div>
</body>
</html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # -------------------------------------------------------------------------
        # KHUSUS UTK FITUR AUTH SERVICE (MENGHASILKAN TOKEN JWT BERBENTUK JSON)
        # -------------------------------------------------------------------------
        if self.path == '/auth':
            # 1. Tentukan isi data (payload) di dalam token
            payload = {
                "iss": JWT_ISSUER,                                            # Target Issuer penentu kecocokan di Kong
                "user_id": 99,
                "role": "mahasiswa",
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30) # Token berlaku 30 menit
            }
            
            # 2. Generate token menggunakan algoritma default HS256
            generated_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
            # 3. Bungkus hasil token ke dalam format JSON response
            response_data = {
                "status": "Login Success via Auth Service",
                "token_type": "Bearer",
                "access_token": generated_token
            }
            response_json = json.dumps(response_data)
            
            # 4. Kirim sebagai JSON data ke client (Postman/Browser)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_json)))
            self.end_headers()
            self.wfile.write(response_json.encode())
            return

        # -------------------------------------------------------------------------
        # UTK SERVICE LAIN (ORDER & PAYMENT) TETAP MENGEMBALIKAN HTML SEPERTI BIASA
        # -------------------------------------------------------------------------
        detected_service = SERVICE_NAME
        if self.path == '/orders':
            detected_service = "Order Service"
        elif self.path == '/payments':
            detected_service = "Payment Service"

        response_html = generate_html(detected_service, self.path)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(response_html)))
        self.end_headers()
        self.wfile.write(response_html.encode())

    def log_message(self, format, *args):
        pass

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', PORT), Handler)
    print(f"{SERVICE_NAME} running on port {PORT}")
    server.serve_forever()
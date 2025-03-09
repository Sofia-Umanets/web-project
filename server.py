from http.server import HTTPServer
from request_handler import HTTPHandler
import logging
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

def main():
    logging.basicConfig(level=logging.DEBUG)
    host = os.environ.get("HOST", "158.160.145.153")
    port = int(os.environ.get("PORT", 8080))

    httpd = HTTPServer((host, port), HTTPHandler)
    logging.info(f"Server started on {host}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
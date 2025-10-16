@echo off
chcp 65001
rem Запуск локального сервера и открытие браузера
cd /d %~dp0

rem Создание кастомного Python сервера с добавлением заголовков
@echo Создание кастомного HTTP сервера
> custom_http_server.py echo import http.server
>> custom_http_server.py echo import socketserver
>> custom_http_server.py echo.
>> custom_http_server.py echo PORT = 8000
>> custom_http_server.py echo.
>> custom_http_server.py echo class CustomHandler(http.server.SimpleHTTPRequestHandler):
>> custom_http_server.py echo ^    def do_GET(self):
>> custom_http_server.py echo ^        if self.path.endswith('.js'):
>> custom_http_server.py echo ^            self.send_response(200)
>> custom_http_server.py echo ^            self.send_header('Content-Type', 'application/javascript')
>> custom_http_server.py echo ^            self.end_headers()
>> custom_http_server.py echo ^            with open(self.translate_path(self.path), 'rb') as file:
>> custom_http_server.py echo ^                self.copyfile(file, self.wfile)
>> custom_http_server.py echo ^        else:
>> custom_http_server.py echo ^            super().do_GET()
>> custom_http_server.py echo ^    def end_headers(self):
>> custom_http_server.py echo ^        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
>> custom_http_server.py echo ^        self.send_header('Pragma', 'no-cache')
>> custom_http_server.py echo ^        self.send_header('Expires', '0')
>> custom_http_server.py echo ^        self.send_header('X-Content-Type-Options', 'nosniff')
>> custom_http_server.py echo ^        super().end_headers()
>> custom_http_server.py echo.
>> custom_http_server.py echo Handler = CustomHandler
>> custom_http_server.py echo.
>> custom_http_server.py echo with socketserver.TCPServer(('', PORT), Handler) as httpd:
>> custom_http_server.py echo ^    print(f"Serving at port {PORT}")
>> custom_http_server.py echo ^    httpd.serve_forever()

rem Запуск Python кастомного HTTP сервера
start /b python custom_http_server.py

rem Задержка на несколько секунд для запуска сервера
ping 127.0.0.1 -n 5 > nul

rem Открытие браузера с адресом http://localhost:8000
start "" "http://localhost:8000/Start.html"

rem Сообщение о завершении
@echo Сервер запущен. Откройте браузер и перейдите по адресу http://localhost:8000
pause
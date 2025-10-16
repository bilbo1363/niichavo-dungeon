import http.server
import socketserver

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.js'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/javascript')
            self.end_headers()
            with open(self.translate_path(self.path), 'rb') as file:
                self.copyfile(file, self.wfile)
        else:
            super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

Handler = CustomHandler

with socketserver.TCPServer(('', PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()

from http.server import HTTPServer, BaseHTTPRequestHandler
from visualizatons import generate_visualizations


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")

    def do_POST(self):
        if self.path == '/visualize':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length).decode('utf-8')
            visualizations = generate_visualizations(data).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(visualizations)


def run():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run()

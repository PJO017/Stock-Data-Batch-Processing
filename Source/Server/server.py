from http.server import HTTPServer, BaseHTTPRequestHandler
from visualizatons import generate_visualizations
import json


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/visualize':
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length).decode('utf-8')
            message = json.dumps(generate_visualizations(data)).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(message)


def run():
    port = 8000
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyRequestHandler)
    print(f"Starting httpd server on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run()

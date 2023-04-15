from http.server import HTTPServer, BaseHTTPRequestHandler
from visualizatons import visualize
import json


class MyRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        data = self.rfile.read(content_length).decode('utf-8')
        message = json.dumps(visualize(data)).encode('utf-8')

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

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run(port=3000):
    # 确保在脚本所在目录运行
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # 切换到 frontend 目录
    if os.path.exists('frontend'):
        os.chdir('frontend')
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f"Frontend server running at http://localhost:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == '__main__':
    port = 3000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run(port) 
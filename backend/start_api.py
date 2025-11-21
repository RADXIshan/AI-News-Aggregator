from app.api import app
import asyncio
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import io


class FastAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that runs FastAPI without external dependencies"""
    
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        self.handle_request()
    
    def handle_request(self):
        try:
            # Parse the path
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            
            # Get request body for POST requests
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Create a mock scope for FastAPI
            scope = {
                "type": "http",
                "method": self.command,
                "path": path,
                "query_string": parsed_path.query.encode(),
                "headers": [(k.lower().encode(), v.encode()) for k, v in self.headers.items()],
            }
            
            # Run the FastAPI app
            response = asyncio.run(self.call_fastapi(scope, body))
            
            # Send response
            self.send_response(response["status"])
            # Don't add CORS headers here - FastAPI middleware handles them
            for key, value in response["headers"].items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response["body"])
            
        except Exception as e:
            print(f"Error handling request: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))
    
    async def call_fastapi(self, scope, body):
        """Call FastAPI app and return response"""
        response_data = {
            "status": 200,
            "headers": {"Content-Type": "application/json"},
            "body": b""
        }
        
        async def receive():
            return {"type": "http.request", "body": body}
        
        async def send(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
                response_data["headers"] = {
                    k.decode(): v.decode() 
                    for k, v in message.get("headers", [])
                }
            elif message["type"] == "http.response.body":
                response_data["body"] += message.get("body", b"")
        
        await app(scope, receive, send)
        return response_data
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"{self.address_string()} - {format % args}")


def run_server(host="0.0.0.0", port=8000):
    """Run the FastAPI app with Python's built-in HTTP server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, FastAPIHandler)
    
    print(f"Starting server on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    run_server(host, port)

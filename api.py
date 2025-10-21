from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "message": "Company enrichment API is running"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        if self.path == '/enrich':
            self.handle_enrich()
        elif self.path == '/webhook':
            self.handle_webhook()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Endpoint not found"}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_enrich(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            domain = data.get('domain')
            list_source = data.get('list_source')
            
            if not domain:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "Domain is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            if not list_source:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "List source is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Mock response
            result = {
                "status": "enriched",
                "company": {
                    "name": "Test Company",
                    "domain": domain,
                    "industry": "Technology",
                    "location": "San Francisco, CA",
                    "employee_count": 100,
                    "linkedin": "https://linkedin.com/company/test"
                },
                "founders": [
                    {
                        "name": "Test Founder",
                        "title": "CEO & Founder",
                        "email": "founder@test.com",
                        "linkedin": "https://linkedin.com/in/test"
                    }
                ],
                "owner": "james@scopvc.com"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Internal server error"}
            self.wfile.write(json.dumps(response).encode())
    
    def handle_webhook(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            domain = data.get('domain')
            list_source = data.get('list_source')
            
            if not domain:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "Domain is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            if not list_source:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"status": "error", "message": "List source is required"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Mock response
            result = {
                "status": "enriched",
                "company": {
                    "name": "Test Company",
                    "domain": domain,
                    "industry": "Technology",
                    "location": "San Francisco, CA",
                    "employee_count": 100,
                    "linkedin": "https://linkedin.com/company/test"
                },
                "founders": [
                    {
                        "name": "Test Founder",
                        "title": "CEO & Founder",
                        "email": "founder@test.com",
                        "linkedin": "https://linkedin.com/in/test"
                    }
                ],
                "owner": "zi@scopvc.com"
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "error", "message": "Internal server error"}
            self.wfile.write(json.dumps(response).encode())
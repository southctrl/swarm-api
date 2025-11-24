from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import urllib.request
import urllib.error

EXTERNAL_API_BASE = "http://192.99.42.71:30058/api"

class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler
    Routes:
    - /api/status -> fetches from external API
    - /api/commands -> fetches from external API
    - /api/commands/{command} -> fetches from external API
    - /api/shards -> fetches from external API
    - /api/servers -> fetches from external API
    """
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            # Parse the path
            path = self.path.split('?')[0]  # Remove query params if any
            
            if path == '/api/status':
                self.handle_status()
            elif path == '/api/commands':
                self.handle_commands()
            elif path.startswith('/api/commands/'):
                command_name = path.split('/api/commands/')[1]
                self.handle_command_details(command_name)
            elif path == '/api/shards':
                self.handle_shards()
            elif path == '/api/servers':
                self.handle_servers()
            else:
                self.send_error_response(404, "Endpoint not found")
        
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def handle_status(self):
        """Fetch and return status from external API"""
        try:
            data = self.fetch_external_api('/status')
            self.send_json_response(data)
        except Exception as e:
            self.send_error_response(500, f"Failed to fetch status: {str(e)}")
    
    def handle_commands(self):
        """Fetch and return commands from external API"""
        try:
            data = self.fetch_external_api('/commands')
            self.send_json_response(data)
        except Exception as e:
            self.send_error_response(500, f"Failed to fetch commands: {str(e)}")
    
    def handle_shards(self):
        """Fetch and return shards from external API"""
        try:
            data = self.fetch_external_api('/shards')
            self.send_json_response(data)
        except Exception as e:
            self.send_error_response(500, f"Failed to fetch shards: {str(e)}")
    
    def handle_servers(self):
        """Fetch and return servers from external API"""
        try:
            data = self.fetch_external_api('/servers')
            self.send_json_response(data)
        except Exception as e:
            self.send_error_response(500, f"Failed to fetch servers: {str(e)}")
    
    def handle_command_details(self, command_name):
        """Fetch and return specific command details from external API"""
        try:
            data = self.fetch_external_api(f'/commands/{command_name}')
            self.send_json_response(data)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.send_error_response(404, f"Command '{command_name}' not found")
            else:
                self.send_error_response(e.code, f"Failed to fetch command: {str(e)}")
        except Exception as e:
            self.send_error_response(500, f"Failed to fetch command: {str(e)}")
    
    def fetch_external_api(self, endpoint):
        """Fetch data from external API"""
        url = f"{EXTERNAL_API_BASE}{endpoint}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            # Re-raise HTTP errors to be handled by caller
            raise
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_body = json.dumps(data, indent=2)
        self.wfile.write(response_body.encode('utf-8'))
    
    def send_error_response(self, status_code, error_message):
        """Send error response"""
        error_data = {
            "success": False,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.send_json_response(error_data, status_code)
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

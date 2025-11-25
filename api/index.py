from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import urllib.request
import urllib.error

API_BASE_URL = 'http://192.99.42.71:30058/api'

class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler
    Routes:
    - /api/status -> fetches bot info from external API shards endpoint
    - /api/commands -> fetches from external API
    - /api/commands/{command} -> fetches from external API
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
            else:
                self.send_error_response(404, "Endpoint not found")
        
        except Exception as e:
            self.send_error_response(500, str(e))
    
    def handle_status(self):
        """Fetch bot status from external API shards endpoint"""
        try:
            # Fetch shard info from external API
            shards_data = self.fetch_external_api('/shards')
            
            # Calculate total servers and members from shards
            total_servers = 0
            total_members = 0
            
            if 'shards' in shards_data and isinstance(shards_data['shards'], list):
                for shard in shards_data['shards']:
                    total_servers += shard.get('server_count', 0)
                    total_members += shard.get('cached_user_count', 0)
            
            # Try to get commands count from external API
            commands_count = 0
            try:
                commands_data = self.fetch_external_api('/commands')
                commands_count = commands_data.get('total_commands', 0)
            except:
                pass  # If external API fails, just use 0
            
            # Format response to match what the frontend expects
            response_data = {
                "success": True,
                "bot": {
                    "name": "Swarm",
                    "id": 1441775100377698315,
                    "avatar": "https://cdn.discordapp.com/avatars/1441775100377698315/a9b49c9bef5f8f073bbc7fd8e4a36a8f.png"
                },
                "status": {
                    "servers": total_servers,
                    "members": total_members,
                    "commands": commands_count,
                    "online": True
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.send_json_response(response_data)
        
        except Exception as e:
            self.send_error_response(500, f"Failed to fetch status: {str(e)}")
    
    def handle_commands(self):
        """Fetch and return commands from external API"""
        try:
            data = self.fetch_external_api('/commands')
            self.send_json_response(data)
        except Exception as e:
            self.send_error_response(500, f"Failed to fetch commands: {str(e)}")
    
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
        url = f"{API_BASE_URL}{endpoint}"
        
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

from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import urllib.request
import urllib.error
import sys
import os

# Configuration - reads from environment variables in Vercel
BOT_TOKEN = os.environ.get('BOT_TOKEN')
API_BASE_URL = os.environ.get('API_BASE_URL', 'http://192.99.42.71:30058/api')

# SSL context to allow insecure HTTP requests from HTTPS
import ssl
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

DISCORD_API_BASE = "https://discord.com/api/v10"

class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler
    Routes:
    - /api/status -> fetches bot info from Discord API using token from config.py
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
        """Fetch bot status from external API"""
        try:
            # Fetch status from external API which has direct bot access
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
    
    def fetch_discord_api(self, endpoint, token):
        """Fetch data from Discord API"""
        url = f"{DISCORD_API_BASE}{endpoint}"
        
        try:
            req = urllib.request.Request(url)
            req.add_header('Authorization', f'Bot {token}')
            req.add_header('Content-Type', 'application/json')
            req.add_header('User-Agent', 'DiscordBot (https://github.com/discord/discord-api-docs, 1.0)')
            req.add_header('Accept', 'application/json')
            req.add_header('Accept-Encoding', 'gzip, deflate')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read()
                return json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            raise Exception(f"Discord API error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
    
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

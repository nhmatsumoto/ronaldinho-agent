import json
import sys
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

# Dictionary to store messages: peer_id -> [messages]
mailbox = defaultdict(list)
LOG_FILE = "signaling.log"

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    print(formatted_msg, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(formatted_msg + "\n")

class SignalingHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        log(f"DEBUG: POST {self.path} from {self.client_address}")
        if self.path == '/send':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                target_id = data.get('targetId')
                msg_type = data.get('type')
                msg_data = data.get('data')
                
                if target_id and msg_type and msg_data:
                    message = {"Type": msg_type, "Data": msg_data}
                    mailbox[target_id].append(message)
                    log(f"[*] Stored message {msg_type} for {target_id}")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok"}).encode())
                    return
                else:
                    log(f"[!] Invalid payload: {data}")
            except Exception as e:
                log(f"[!] Error processing POST: {e}")
        
        self.send_response(400)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/receive':
            query = parse_qs(parsed_path.query)
            peer_id = query.get('peerId', [None])[0]
            
            if peer_id:
                messages = mailbox[peer_id]
                mailbox[peer_id] = []
                if messages:
                    log(f"[*] Delivering {len(messages)} messages to {peer_id}")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(messages).encode())
                return
        
        self.send_response(400)
        self.end_headers()

    def log_message(self, format, *args):
         # log(f"HTTP: {format%args}")
         pass

if __name__ == '__main__':
    port = 3000
    # Clear log file on start
    with open(LOG_FILE, "w") as f:
        f.write(f"--- Signaling Server Started at {datetime.datetime.now()} ---\n")
    
    server = HTTPServer(('', port), SignalingHandler)
    log(f"🚀 P2P Signaling Server running on all interfaces at port {port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log("\nStopping signaling server...")
        server.server_close()

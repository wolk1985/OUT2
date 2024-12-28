import json
import hmac
import hashlib
import base64

def generate_signature(timestamp, method, request_path, body, secret_key):
    body_str = json.dumps(body) if body else ''
    message = timestamp + method + request_path + body_str
    mac = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256)
    return base64.b64encode(mac.digest()).decode('utf-8')
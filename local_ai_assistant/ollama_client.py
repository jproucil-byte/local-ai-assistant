"""Local Ollama chat API. No cloud calls; loopback endpoint only."""
import base64
import ipaddress
import json
import urllib.parse
import urllib.request

def local_endpoint(endpoint: str) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    host = parsed.hostname
    if parsed.scheme != 'http' or not host:
        raise ValueError('Only local HTTP Ollama endpoints are supported.')
    try:
        if not ipaddress.ip_address(host).is_loopback:
            raise ValueError('Ollama endpoint must be loopback.')
    except ValueError:
        if host != 'localhost':
            raise ValueError('Ollama endpoint must be loopback.')
    if parsed.username or parsed.password or parsed.path not in ('', '/') or parsed.query or parsed.fragment:
        raise ValueError('Invalid Ollama endpoint.')
    return endpoint.rstrip('/')

def chat(endpoint: str, model: str, messages: list[dict], screenshot: bytes | None = None,
         extended_thinking: bool = False) -> str:
    if not model.strip():
        raise ValueError('Select a model first.')
    payload_messages = [dict(m) for m in messages]
    if screenshot:
        payload_messages[-1]['images'] = [base64.b64encode(screenshot).decode('ascii')]
    request_data = {'model': model, 'messages': payload_messages, 'stream': False,
                    'options': {'num_ctx': 4096}}
    if model.partition(':')[0] == 'qwen3.5':
        request_data['think'] = extended_thinking
    payload = json.dumps(request_data).encode('utf-8')
    req = urllib.request.Request(local_endpoint(endpoint) + '/api/chat', data=payload,
                                 headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=180) as response:
        result = json.load(response)
    return result.get('message', {}).get('content', '').strip() or '(Model returned no text.)'

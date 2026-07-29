"""Test different Bearer Token formats and models."""
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv
load_dotenv()
import os

full_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK', '')
# Try without the "bedrock-api-key-" prefix
base64_only = full_token.replace('bedrock-api-key-', '')
region = 'us-west-2'

models_to_try = [
    'anthropic.claude-3-sonnet-20240229-v1:0',
    'anthropic.claude-3-haiku-20240307-v1:0',
    'amazon.nova-pro-v1:0',
    'amazon.nova-lite-v1:0',
]

tokens_to_try = [
    ('full token', full_token),
    ('base64 only (no prefix)', base64_only),
]

payload = {
    'messages': [{'role': 'user', 'content': [{'text': 'Say hi'}]}],
    'inferenceConfig': {'maxTokens': 50, 'temperature': 0.7}
}

for token_name, token in tokens_to_try:
    print(f"\n{'='*50}")
    print(f"Token: {token_name} ({len(token)} chars)")
    print(f"{'='*50}")
    
    for model in models_to_try:
        url = f'https://bedrock-runtime.{region}.amazonaws.com/model/{model}/converse'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}',
        }
        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read().decode('utf-8'))
                text = body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
                print(f"  {model}: SUCCESS -> {text[:50]}")
        except urllib.error.HTTPError as e:
            err = ''
            try:
                err = e.read().decode('utf-8')[:100]
            except:
                pass
            print(f"  {model}: {e.code} -> {err}")
        except Exception as e:
            print(f"  {model}: ERROR -> {str(e)[:80]}")

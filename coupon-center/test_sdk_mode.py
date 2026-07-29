"""Test SDK mode by extracting credentials from the Bearer Token."""
import base64
import urllib.parse
from dotenv import load_dotenv
load_dotenv()
import os
import boto3

full_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK', '')
base64_part = full_token.replace('bedrock-api-key-', '')

# Decode the token to extract credentials
decoded = base64.b64decode(base64_part).decode()
print(f"Decoded URL: {decoded[:100]}...")

# Parse the query parameters
params = urllib.parse.parse_qs(urllib.parse.urlparse('https://' + decoded).query)
print(f"\nParams found: {list(params.keys())}")

# Extract credential info
credential = params.get('X-Amz-Credential', [''])[0]
session_token = params.get('X-Amz-Security-Token', [''])[0]

print(f"Credential: {credential[:40]}...")
print(f"Session Token: {session_token[:40]}...")

# Parse AccessKeyId from credential (format: AKID/date/region/service/aws4_request)
access_key = credential.split('/')[0] if credential else ''
print(f"Access Key ID: {access_key}")

# Try using these as SDK credentials
print(f"\n--- Testing SDK with extracted credentials ---")
try:
    client = boto3.client(
        'bedrock-runtime',
        region_name='us-west-2',
        aws_access_key_id=access_key,
        aws_secret_access_key='dummy',  # We don't have the secret key
        aws_session_token=session_token,
    )
    response = client.converse(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        messages=[{'role': 'user', 'content': [{'text': 'Say hi'}]}],
        inferenceConfig={'maxTokens': 50}
    )
    text = response['output']['message']['content'][0]['text']
    print(f"SUCCESS: {text}")
except Exception as e:
    print(f"Error: {e}")
    print("\nNote: Cannot use SDK mode without the actual Secret Access Key.")
    print("The Bearer Token only contains a pre-signed URL, not raw credentials.")
    print("\nYou need to either:")
    print("1. Get AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY + AWS_SESSION_TOKEN from Workshop console")
    print("2. Or ask the Workshop admin to enable bedrock:CallWithBearerToken permission")

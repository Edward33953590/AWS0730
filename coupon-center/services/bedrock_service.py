"""Bedrock AI service - wraps AWS Bedrock Converse API calls.

Supports two modes:
1. SDK credentials mode: uses boto3 with AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
2. API Key (Bearer Token) mode: uses HTTP POST with Authorization: Bearer <token>

Priority: If AWS_BEARER_TOKEN_BEDROCK is set, use API Key mode. Otherwise use SDK mode.
"""
import json
import os
import urllib.request
import urllib.error
import urllib.parse
import boto3
from botocore.exceptions import ClientError, ReadTimeoutError, ConnectTimeoutError


class BedrockService:
    """Amazon Bedrock AI service with SDK and API Key (Bearer Token) support."""

    def __init__(self):
        self._client = None

    @property
    def region(self):
        return os.getenv('BEDROCK_REGION', os.getenv('AWS_REGION', 'us-east-1'))

    @property
    def default_model(self):
        return os.getenv('DEFAULT_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

    @property
    def bearer_token(self):
        return os.getenv('AWS_BEARER_TOKEN_BEDROCK', '')

    @property
    def use_api_key_mode(self):
        """Check if Bearer Token mode is available."""
        return bool(self.bearer_token)

    @property
    def client(self):
        """Boto3 client for SDK mode."""
        if self._client is None:
            try:
                self._client = boto3.client(
                    'bedrock-runtime',
                    region_name=self.region,
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID') or None,
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY') or None,
                )
            except Exception:
                self._client = None
        return self._client

    def converse(self, messages, model_id=None, max_tokens=1024):
        """
        Send a conversation to Bedrock Converse API.
        Auto-selects API Key mode or SDK mode.
        Returns (response_text, error).
        """
        model = model_id or self.default_model

        if self.use_api_key_mode:
            return self._converse_with_bearer_token(model, messages, max_tokens)
        else:
            return self._converse_with_sdk(model, messages, max_tokens)

    def _converse_with_bearer_token(self, model_id, messages, max_tokens):
        """API Key mode: HTTP POST with Bearer Token."""
        url = f'https://bedrock-runtime.{self.region}.amazonaws.com/model/{model_id}/converse'

        payload = {
            'messages': [
                {'role': msg['role'], 'content': [{'text': msg['content']}]}
                for msg in messages
            ],
            'inferenceConfig': {
                'maxTokens': max_tokens,
                'temperature': 0.7,
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.bearer_token}',
        }

        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read().decode('utf-8'))

            content = body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
            return content, None

        except urllib.error.HTTPError as e:
            error_body = ''
            try:
                error_body = e.read().decode('utf-8')
            except Exception:
                pass
            return None, f'Bedrock API error ({e.code}): {error_body[:200]}'
        except urllib.error.URLError as e:
            return None, f'Bedrock connection error: {str(e)}'
        except Exception as e:
            return None, f'AI service error: {str(e)}'

    def _converse_with_sdk(self, model_id, messages, max_tokens):
        """SDK credentials mode: uses boto3 BedrockRuntimeClient."""
        if not self.client:
            return None, 'Bedrock client not configured (no AWS credentials or Bearer Token)'

        try:
            converse_messages = [
                {'role': msg['role'], 'content': [{'text': msg['content']}]}
                for msg in messages
            ]

            response = self.client.converse(
                modelId=model_id,
                messages=converse_messages,
                inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.7}
            )

            output = response.get('output', {}).get('message', {})
            content = output.get('content', [{}])[0].get('text', '')
            return content, None

        except (ClientError, ReadTimeoutError, ConnectTimeoutError) as e:
            return None, f'Bedrock SDK error: {str(e)}'
        except Exception as e:
            return None, f'AI service error: {str(e)}'

    def generate_json(self, prompt, model_id=None):
        """
        Send prompt expecting JSON response.
        Returns (parsed_dict, error).
        """
        messages = [{'role': 'user', 'content': prompt}]
        text, error = self.converse(messages, model_id=model_id)
        if error:
            return None, error

        # Try to parse JSON from response
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            return json.loads(text.strip()), None
        except (json.JSONDecodeError, IndexError):
            return {'raw_text': text}, None

    def list_models(self):
        """List available Bedrock models. Returns list of model info dicts."""
        try:
            bedrock_client = boto3.client(
                'bedrock',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID') or None,
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY') or None,
            )
            response = bedrock_client.list_foundation_models()
            models = []
            for m in response.get('modelSummaries', []):
                if 'TEXT' in (m.get('outputModalities') or []):
                    models.append({
                        'modelId': m.get('modelId', ''),
                        'modelName': m.get('modelName', ''),
                        'provider': m.get('providerName', ''),
                    })
            return models
        except Exception:
            return [
                {'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0', 'modelName': 'Claude 3 Sonnet', 'provider': 'Anthropic'},
                {'modelId': 'anthropic.claude-3-haiku-20240307-v1:0', 'modelName': 'Claude 3 Haiku', 'provider': 'Anthropic'},
                {'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Amazon Nova Pro', 'provider': 'Amazon'},
            ]


# Singleton instance
bedrock_service = BedrockService()

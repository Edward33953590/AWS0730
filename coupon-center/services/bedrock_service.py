"""Bedrock AI service - wraps AWS Bedrock Converse API calls."""
import json
import os
import boto3
from botocore.exceptions import ClientError, ReadTimeoutError, ConnectTimeoutError


class BedrockService:
    """Amazon Bedrock AI service with SDK and API Key support."""

    def __init__(self):
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.default_model = os.getenv('DEFAULT_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self._client = None

    @property
    def client(self):
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
        Returns (response_text, error).
        """
        if not self.client:
            return None, 'Bedrock client not configured'

        model = model_id or self.default_model

        try:
            converse_messages = [
                {
                    'role': msg['role'],
                    'content': [{'text': msg['content']}]
                }
                for msg in messages
            ]

            response = self.client.converse(
                modelId=model,
                messages=converse_messages,
                inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.7}
            )

            output = response.get('output', {}).get('message', {})
            content = output.get('content', [{}])[0].get('text', '')
            return content, None

        except (ClientError, ReadTimeoutError, ConnectTimeoutError) as e:
            return None, f'Bedrock error: {str(e)}'
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
            # Handle markdown code blocks
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            return json.loads(text.strip()), None
        except (json.JSONDecodeError, IndexError):
            # Return raw text as fallback
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
            # Return default known models when API unavailable
            return [
                {'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0', 'modelName': 'Claude 3 Sonnet', 'provider': 'Anthropic'},
                {'modelId': 'anthropic.claude-3-haiku-20240307-v1:0', 'modelName': 'Claude 3 Haiku', 'provider': 'Anthropic'},
            ]


# Singleton instance
bedrock_service = BedrockService()

"""Bedrock AI service - wraps AWS Bedrock Converse API calls.

Supports two modes:
1. SDK credentials mode: uses boto3 with AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
2. API Key (Bearer Token) mode: uses HTTP POST with Authorization: Bearer <token>

Priority: If AWS_BEARER_TOKEN_BEDROCK is set, use API Key mode. Otherwise use SDK mode.
"""
import json
import logging
import os
import urllib.request
import urllib.error
import urllib.parse
import boto3
from botocore.exceptions import ClientError, ReadTimeoutError, ConnectTimeoutError

# Configure logger for bedrock service
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Ensure logs are visible in console
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s][BedrockService][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


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
            except Exception as e:
                logger.error(f'Failed to create boto3 client: {e}')
                self._client = None
        return self._client

    def converse(self, messages, model_id=None, max_tokens=1024):
        """
        Send a conversation to Bedrock Converse API.
        Auto-selects API Key mode or SDK mode.
        Returns (response_text, error).
        """
        model = model_id or self.default_model
        logger.info(f'converse() called - model={model}, mode={"bearer_token" if self.use_api_key_mode else "sdk"}, messages_count={len(messages)}')

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

        logger.info(f'[BearerToken] Request URL: {url}')
        logger.info(f'[BearerToken] Region: {self.region}, Model: {model_id}, MaxTokens: {max_tokens}')
        logger.debug(f'[BearerToken] Token length: {len(self.bearer_token)}, first 30 chars: {self.bearer_token[:30]}...')
        logger.debug(f'[BearerToken] Payload: {json.dumps(payload, ensure_ascii=False)[:500]}')

        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')

            logger.info('[BearerToken] Sending HTTP request...')
            with urllib.request.urlopen(req, timeout=60) as resp:
                status_code = resp.getcode()
                raw_body = resp.read().decode('utf-8')

                logger.info(f'[BearerToken] Response status: {status_code}')
                logger.info(f'[BearerToken] Response body length: {len(raw_body)}')
                logger.debug(f'[BearerToken] Response headers: {dict(resp.headers)}')

                if not raw_body:
                    logger.error('[BearerToken] Response body is EMPTY! API returned 200 with no content.')
                    return None, 'Bedrock API returned empty response body (status 200 but no content)'

                logger.debug(f'[BearerToken] Response body (first 500 chars): {raw_body[:500]}')

                body = json.loads(raw_body)
                logger.debug(f'[BearerToken] Parsed response keys: {list(body.keys())}')

                content = body.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', '')
                input_tokens = body.get('usage', {}).get('inputTokens')
                output_tokens = body.get('usage', {}).get('outputTokens')

                logger.info(f'[BearerToken] SUCCESS - content length: {len(content)}, input_tokens: {input_tokens}, output_tokens: {output_tokens}')

                if not content:
                    logger.warning(f'[BearerToken] Content is empty despite valid response. Full body: {raw_body[:1000]}')

                return content, None

        except urllib.error.HTTPError as e:
            error_body = ''
            try:
                error_body = e.read().decode('utf-8')
            except Exception:
                pass

            logger.error(f'[BearerToken] HTTP Error {e.code}')
            logger.error(f'[BearerToken] Error headers: {dict(e.headers)}')
            logger.error(f'[BearerToken] Error body: {error_body[:500]}')

            # Parse error details
            error_message = error_body[:200]
            try:
                error_json = json.loads(error_body)
                error_message = error_json.get('Message', error_json.get('message', error_body[:200]))
                logger.error(f'[BearerToken] Error JSON parsed: {error_json}')
            except (json.JSONDecodeError, ValueError):
                pass

            # Provide specific error messages
            if e.code == 403:
                if 'expired' in error_body.lower():
                    logger.error('[BearerToken] >>> BEARER TOKEN HAS EXPIRED! Please generate a new token. <<<')
                    return None, f'Bearer Token已过期，请重新生成Token。原始错误: {error_message}'
                return None, f'访问被拒绝(403): {error_message}'
            elif e.code == 401:
                return None, f'认证失败(401): {error_message}'
            elif e.code == 404:
                return None, f'模型不存在或未开通(404): {error_message}'
            elif e.code == 429:
                return None, f'请求频率过高(429)，请稍后再试: {error_message}'

            return None, f'Bedrock API error ({e.code}): {error_message}'

        except urllib.error.URLError as e:
            logger.error(f'[BearerToken] URL Error: {e.reason}')
            return None, f'Bedrock connection error: {str(e)}'
        except json.JSONDecodeError as e:
            logger.error(f'[BearerToken] JSON decode error: {e}')
            return None, f'Bedrock API返回了非JSON响应: {str(e)}'
        except Exception as e:
            logger.error(f'[BearerToken] Unexpected error: {type(e).__name__}: {e}', exc_info=True)
            return None, f'AI service error: {str(e)}'

    def _converse_with_sdk(self, model_id, messages, max_tokens):
        """SDK credentials mode: uses boto3 BedrockRuntimeClient."""
        if not self.client:
            logger.error('[SDK] Bedrock client is None - no AWS credentials configured')
            return None, 'Bedrock client not configured (no AWS credentials or Bearer Token)'

        logger.info(f'[SDK] Calling converse - model={model_id}, max_tokens={max_tokens}')

        try:
            converse_messages = [
                {'role': msg['role'], 'content': [{'text': msg['content']}]}
                for msg in messages
            ]

            logger.debug(f'[SDK] Messages: {json.dumps(converse_messages, ensure_ascii=False)[:500]}')

            response = self.client.converse(
                modelId=model_id,
                messages=converse_messages,
                inferenceConfig={'maxTokens': max_tokens, 'temperature': 0.7}
            )

            logger.debug(f'[SDK] Response keys: {list(response.keys())}')

            output = response.get('output', {}).get('message', {})
            content = output.get('content', [{}])[0].get('text', '')
            input_tokens = response.get('usage', {}).get('inputTokens')
            output_tokens = response.get('usage', {}).get('outputTokens')

            logger.info(f'[SDK] SUCCESS - content length: {len(content)}, input_tokens: {input_tokens}, output_tokens: {output_tokens}')

            if not content:
                logger.warning(f'[SDK] Content is empty. Full output: {output}')

            return content, None

        except (ClientError, ReadTimeoutError, ConnectTimeoutError) as e:
            logger.error(f'[SDK] Client error: {type(e).__name__}: {e}')
            return None, f'Bedrock SDK error: {str(e)}'
        except Exception as e:
            logger.error(f'[SDK] Unexpected error: {type(e).__name__}: {e}', exc_info=True)
            return None, f'AI service error: {str(e)}'

    def generate_json(self, prompt, model_id=None):
        """
        Send prompt expecting JSON response.
        Returns (parsed_dict, error).
        """
        logger.info(f'generate_json() called - prompt length: {len(prompt)}, model_id: {model_id}')
        messages = [{'role': 'user', 'content': prompt}]
        text, error = self.converse(messages, model_id=model_id)
        if error:
            logger.error(f'generate_json() converse returned error: {error}')
            return None, error

        logger.info(f'generate_json() got text response, length: {len(text) if text else 0}')
        logger.debug(f'generate_json() raw text: {text[:300] if text else "None"}')

        if not text:
            logger.error('generate_json() text is empty/None after converse succeeded')
            return None, 'AI返回了空内容'

        # Try to parse JSON from response
        try:
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            result = json.loads(text.strip())
            logger.info(f'generate_json() JSON parsed successfully, keys: {list(result.keys()) if isinstance(result, dict) else "list"}')
            return result, None
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f'generate_json() JSON parse failed: {e}, returning raw_text')
            return {'raw_text': text}, None

    def list_models(self):
        """List available Bedrock models. Returns list of model info dicts."""
        logger.info('list_models() called')
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
            logger.info(f'list_models() found {len(models)} text models')
            return models
        except Exception as e:
            logger.error(f'list_models() failed: {e}, returning fallback list')
            return [
                {'modelId': 'anthropic.claude-3-sonnet-20240229-v1:0', 'modelName': 'Claude 3 Sonnet', 'provider': 'Anthropic'},
                {'modelId': 'anthropic.claude-3-haiku-20240307-v1:0', 'modelName': 'Claude 3 Haiku', 'provider': 'Anthropic'},
                {'modelId': 'amazon.nova-pro-v1:0', 'modelName': 'Amazon Nova Pro', 'provider': 'Amazon'},
            ]


# Singleton instance
bedrock_service = BedrockService()

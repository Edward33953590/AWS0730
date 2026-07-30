"""AI service - wraps DeepSeek API calls via OpenAI-compatible client.

Replaces the original AWS Bedrock integration. Uses the OpenAI Python SDK
to call DeepSeek's API endpoint.
"""
import json
import logging
import os
from openai import OpenAI

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s][DeepSeekService][%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class BedrockService:
    """AI service using DeepSeek API (OpenAI-compatible).

    Maintains the same interface as the original Bedrock service for
    backward compatibility with all callers.
    """

    def __init__(self):
        self._client = None

    @property
    def default_model(self):
        return os.getenv('DEEPSEEK_MODEL', 'deepseek-v4-flash')

    @property
    def api_key(self):
        return os.getenv('DEEPSEEK_API_KEY', '')

    @property
    def base_url(self):
        return os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')

    @property
    def client(self):
        """Lazy-initialized OpenAI client pointing to DeepSeek."""
        if self._client is None:
            key = self.api_key
            if not key:
                logger.error('DEEPSEEK_API_KEY is not set!')
                return None
            self._client = OpenAI(
                api_key=key,
                base_url=self.base_url,
            )
        return self._client

    def converse(self, messages, model_id=None, max_tokens=1024):
        """
        Send a conversation to DeepSeek API.
        messages: list of {'role': 'user'|'assistant'|'system', 'content': str}
        Returns (response_text, error).
        """
        model = model_id or self.default_model
        logger.info(f'converse() called - model={model}, messages_count={len(messages)}')

        if not self.client:
            return None, 'DeepSeek API 未配置（缺少 DEEPSEEK_API_KEY）'

        try:
            # Build messages for OpenAI-compatible API
            api_messages = []
            for msg in messages:
                api_messages.append({
                    'role': msg['role'],
                    'content': msg['content'],
                })

            logger.debug(f'Sending request to DeepSeek - model={model}, max_tokens={max_tokens}')

            response = self.client.chat.completions.create(
                model=model,
                messages=api_messages,
                max_tokens=max_tokens,
                temperature=0.7,
                stream=False,
            )

            content = response.choices[0].message.content or ''
            usage = response.usage
            logger.info(
                f'converse() SUCCESS - content length: {len(content)}, '
                f'input_tokens: {usage.prompt_tokens if usage else "N/A"}, '
                f'output_tokens: {usage.completion_tokens if usage else "N/A"}'
            )

            if not content:
                logger.warning('converse() returned empty content')
                return None, 'AI 返回了空内容'

            return content, None

        except Exception as e:
            error_msg = f'DeepSeek API error: {type(e).__name__}: {str(e)}'
            logger.error(error_msg, exc_info=True)
            return None, error_msg

    def generate_json(self, prompt, model_id=None):
        """
        Send prompt expecting JSON response.
        Returns (parsed_dict, error).
        """
        logger.info(f'generate_json() called - prompt length: {len(prompt)}, model_id: {model_id}')

        # Use system message to encourage JSON output
        messages = [
            {'role': 'system', 'content': '你是一个有用的助手。请严格按照用户要求的JSON格式返回结果，不要添加额外的解释文字。'},
            {'role': 'user', 'content': prompt},
        ]

        text, error = self.converse(messages, model_id=model_id)
        if error:
            logger.error(f'generate_json() converse returned error: {error}')
            return None, error

        logger.info(f'generate_json() got text response, length: {len(text) if text else 0}')
        logger.debug(f'generate_json() raw text: {text[:300] if text else "None"}')

        if not text:
            logger.error('generate_json() text is empty/None after converse succeeded')
            return None, 'AI 返回了空内容'

        # Try to parse JSON from response
        try:
            # Strip markdown code fences if present
            clean_text = text.strip()
            if '```json' in clean_text:
                clean_text = clean_text.split('```json')[1].split('```')[0]
            elif '```' in clean_text:
                clean_text = clean_text.split('```')[1].split('```')[0]

            result = json.loads(clean_text.strip())
            logger.info(f'generate_json() JSON parsed successfully, keys: {list(result.keys()) if isinstance(result, dict) else "list"}')
            return result, None
        except (json.JSONDecodeError, IndexError) as e:
            logger.warning(f'generate_json() JSON parse failed: {e}, returning raw_text')
            return {'raw_text': text}, None

    def list_models(self):
        """List available models. Returns a static list for DeepSeek."""
        return [
            {'modelId': 'deepseek-v4-flash', 'modelName': 'DeepSeek V4 Flash', 'provider': 'DeepSeek'},
            {'modelId': 'deepseek-v4-pro', 'modelName': 'DeepSeek V4 Pro', 'provider': 'DeepSeek'},
        ]


# Singleton instance
bedrock_service = BedrockService()

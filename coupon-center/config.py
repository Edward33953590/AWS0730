import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///coupon_center.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-dev-secret')
    JWT_EXPIRES_HOURS = int(os.getenv('JWT_EXPIRES_HOURS', '168'))

    # AWS Bedrock
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    BEDROCK_API_KEY = os.getenv('BEDROCK_API_KEY', '')
    BEDROCK_REGION = os.getenv('BEDROCK_REGION', 'us-east-1')
    DEFAULT_MODEL_ID = os.getenv('DEFAULT_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')

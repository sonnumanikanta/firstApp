import jwt
from datetime import datetime, timedelta
from django.conf import settings

def create_access_token(payload: dict) -> str:
    exp = datetime.utcnow() + timedelta(minutes=settings.JWT_SETTINGS['ACCESS_EXP_MINUTES'])
    payload = {**payload, 'type': 'access', 'exp': exp}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_SETTINGS['ALGORITHM'])

def create_refresh_token(payload: dict) -> str:
    exp = datetime.utcnow() + timedelta(days=settings.JWT_SETTINGS['REFRESH_EXP_DAYS'])
    payload = {**payload, 'type': 'refresh', 'exp': exp}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_SETTINGS['ALGORITHM'])

def verify_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_SETTINGS['ALGORITHM']])
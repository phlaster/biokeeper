import jwt
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import JWT_PUBLIC_KEY

def verify_jwt_token(token):
    payload = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=['RS256'])
    return payload

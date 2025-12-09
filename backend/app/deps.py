from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings
from .models import Base
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db():
    Base.metadata.create_all(bind=engine)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def hash_password(passwd):
    return pwd_context.hash(passwd)

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return token

def decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

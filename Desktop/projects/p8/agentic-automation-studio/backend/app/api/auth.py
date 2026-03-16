from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import csv
import os
from pathlib import Path
from typing import Optional

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret key for JWT (in production, use environment variable)
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days

# CSV file path for user storage
USERS_CSV_PATH = Path(__file__).parent.parent.parent / "data" / "users.csv"

# Ensure data directory exists
USERS_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)

# Initialize CSV file if it doesn't exist
if not USERS_CSV_PATH.exists():
    with open(USERS_CSV_PATH, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['email', 'hashed_password', 'name', 'created_at'])


class UserSignup(BaseModel):
    email: EmailStr
    password: str
    name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user from CSV by email"""
    if not USERS_CSV_PATH.exists():
        return None
    
    with open(USERS_CSV_PATH, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == email:
                return row
    return None


def create_user(email: str, hashed_password: str, name: str):
    """Add new user to CSV"""
    with open(USERS_CSV_PATH, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([email, hashed_password, name, datetime.utcnow().isoformat()])


@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password length
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Hash password and create user
    hashed_password = hash_password(user_data.password)
    create_user(user_data.email, hashed_password, user_data.name)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user_data.email,
            "name": user_data.name
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    # Get user from CSV
    user = get_user_by_email(credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user['email'],
            "name": user['name']
        }
    }


@router.get("/me")
async def get_current_user(token: Optional[str] = None):
    """Get current user from token"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token required"
        )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "email": user['email'],
        "name": user['name']
    }

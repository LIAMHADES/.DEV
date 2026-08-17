"""
Authentication routes: register and login by phone number.
"""
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
import bcrypt

from database import get_db
from models import User
from schemas import UserCreate, UserResponse, Token
from config import settings

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def _ensure_bcrypt_length(password: str) -> bytes:
    password_bytes = (password or "").encode("utf-8")
    if len(password_bytes) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password too long (bcrypt limit is 72 bytes)",
        )
    return password_bytes


def get_password_hash(password: str) -> str:
    password_bytes = _ensure_bcrypt_length(password)
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user by phone number."""
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    hashed_pw = None
    if user_data.password:
        hashed_pw = get_password_hash(user_data.password)

    user = User(phone=user_data.phone, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """Login and get access token."""
    user = db.query(User).filter(User.phone == user_data.phone).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # If password is set, verify it
    if user.hashed_password and user_data.password:
        password_bytes = _ensure_bcrypt_length(user_data.password)
        if not bcrypt.checkpw(password_bytes, user.hashed_password.encode("utf-8")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )

    access_token = create_access_token(
        data={"sub": user.phone, "user_id": user.id})
    return Token(access_token=access_token)


# --- Dependency ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

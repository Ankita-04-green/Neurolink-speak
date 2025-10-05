import streamlit as st
import hashlib
import sqlite3
import jwt
import datetime
from database import User, get_db
from config import config
from typing import Optional

# Secret key for JWT (in production, use a more secure method to store this)
SECRET_KEY = "neurolink_speak_secret_key_change_this_in_production"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(plain_password) == hashed_password

def create_user(username: str, email: str, password: str, 
                native_language: str = None, target_language: str = None, 
                voice_type: str = None) -> Optional[User]:
    """Create a new user in the database"""
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            return None
            
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            return None
            
        # Create new user
        new_user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            native_language=native_language or config.DEFAULT_SOURCE_LANGUAGE,
            target_language=target_language or config.DEFAULT_TARGET_LANGUAGE,
            voice_type=voice_type or "default"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
        return None
    finally:
        # Close the database connection
        try:
            next(db_generator)
        except StopIteration:
            pass

def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password"""
    db_generator = get_db()
    db = next(db_generator)
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
            
        if verify_password(password, user.hashed_password):
            return user
        return None
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None
    finally:
        # Close the database connection
        try:
            next(db_generator)
        except StopIteration:
            pass

def login_user(user: User) -> str:
    """Create a JWT token for a logged-in user"""
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return the payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user() -> Optional[User]:
    """Get the current user from session state"""
    if "user" in st.session_state:
        return st.session_state.user
    return None

def login_form():
    """Display the login form"""
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = user
                st.session_state.token = login_user(user)
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

def signup_form():
    """Display the signup form"""
    with st.form("signup_form"):
        st.subheader("Sign Up")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        # Language preferences
        native_language = st.selectbox(
            "Native Language", 
            config.SUPPORTED_LANGUAGES, 
            index=config.SUPPORTED_LANGUAGES.index(config.DEFAULT_SOURCE_LANGUAGE)
        )

        # 🧠 Conditionally show Target Language based on translation toggle
        if st.session_state.get("translation_enabled", True):
            target_language_options = config.SUPPORTED_LANGUAGES + ["none"]
            target_language = st.selectbox(
                "Target Language", 
                target_language_options, 
                index=target_language_options.index(config.DEFAULT_TARGET_LANGUAGE)
                if config.DEFAULT_TARGET_LANGUAGE in target_language_options else 0
            )
        else:
            target_language = native_language  # fallback when translation is disabled
            st.info("Translation is disabled — Target Language set to Native Language automatically.")
        
        voice_type = st.selectbox("Voice Type", ["default", "male", "female"])
        
        signup_button = st.form_submit_button("Sign Up")
        
        if signup_button:
            if password != confirm_password:
                st.error("Passwords do not match")
                return
                
            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return
                
            user = create_user(username, email, password, native_language, target_language, voice_type)
            if user:
                st.session_state.user = user
                st.session_state.token = login_user(user)
                st.success("Account created successfully!")
                st.rerun()
            else:
                st.error("Username or email already exists")

def logout():
    """Logout the current user"""
    if "user" in st.session_state:
        del st.session_state.user
    if "token" in st.session_state:
        del st.session_state.token
    st.success("You have been logged out")
    st.rerun()

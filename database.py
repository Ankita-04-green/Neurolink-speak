from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import config

# Create base class for SQLAlchemy models
Base = declarative_base()

# User model for authentication
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    native_language = Column(String, default=config.DEFAULT_SOURCE_LANGUAGE)
    target_language = Column(String, default=config.DEFAULT_TARGET_LANGUAGE)
    voice_type = Column(String, default="default")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

# Conversation log model
class ConversationLog(Base):
    __tablename__ = 'conversation_logs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    direction = Column(String)  # "outgoing" (EEG/EMG to speech) or "incoming" (speech to text)
    original_text = Column(Text)
    translated_text = Column(Text)
    audio_file_path = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<ConversationLog(id={self.id}, user_id={self.user_id}, direction='{self.direction}')>"

# Create database engine and session
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5000/veritrust')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class VideoAnalysis(Base):
    """
    Stores video analysis results with hash-based deduplication
    """
    __tablename__ = "video_analyses"

    id = Column(Integer, primary_key=True, index=True)
    
    # Video identification
    video_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA-256 hash
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)  # bytes
    
    # Analysis results
    prediction = Column(String(20), nullable=False)  # REAL, FAKE, SUSPICIOUS
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Blockchain verification
    blockchain_tx_hash = Column(String(66), unique=True, index=True)  # Ethereum tx hash
    blockchain_verified = Column(Boolean, default=False)
    blockchain_url = Column(String(255))  # Etherscan/Polygonscan URL
    
    # Metadata
    analysis_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    analysis_duration = Column(Float)  # seconds
    model_version = Column(String(50), default="efficientnet_b0_v1")
    
    # Additional data
    gradcam_generated = Column(Boolean, default=False)
    notes = Column(Text)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'video_hash': self.video_hash,
            'filename': self.filename,
            'file_size': self.file_size,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'blockchain_tx_hash': self.blockchain_tx_hash,
            'blockchain_verified': self.blockchain_verified,
            'blockchain_url': self.blockchain_url,
            'analysis_timestamp': self.analysis_timestamp.isoformat() if self.analysis_timestamp else None,
            'analysis_duration': self.analysis_duration,
            'model_version': self.model_version,
            'gradcam_generated': self.gradcam_generated
        }


class BlockchainLog(Base):
    """
    Logs all blockchain transactions for audit trail
    """
    __tablename__ = "blockchain_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Transaction details
    tx_hash = Column(String(66), unique=True, index=True)
    video_hash = Column(String(64), index=True, nullable=False)
    
    # What was logged
    is_fake = Column(Boolean, nullable=False)
    confidence = Column(Integer, nullable=False)  # 0-100
    
    # Blockchain metadata
    block_number = Column(Integer)
    gas_used = Column(Integer)
    transaction_cost = Column(String(50))  # in ETH/MATIC
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = Column(DateTime)
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    error_message = Column(Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tx_hash': self.tx_hash,
            'video_hash': self.video_hash,
            'is_fake': self.is_fake,
            'confidence': self.confidence,
            'block_number': self.block_number,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }


def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def get_db():
    """
    Get database session (for FastAPI dependency injection)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Create tables when run directly
    print("Initializing VeriTrust database...")
    init_db()
    print("Database ready!")
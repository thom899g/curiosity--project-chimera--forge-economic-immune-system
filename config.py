"""
Project Chimera Configuration Manager
Centralized configuration with environment variable fallbacks
Architectural Choice: Pydantic for runtime type validation and schema enforcement
"""
import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseSettings, Field, validator
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ChimeraConfig(BaseSettings):
    """Immutable configuration class with validation"""
    
    # Firebase Configuration (CRITICAL: Primary state management)
    firebase_credential_path: str = Field(
        default="config/firebase-service-account.json",
        description="Path to Firebase service account credentials"
    )
    firestore_collection_prefix: str = "chimera_"
    
    # Blockchain Configuration
    l2_rpc_url: str = Field(
        default="https://polygon-mainnet.g.alchemy.com/v2/",
        description="Low-fee L2 RPC endpoint (Polygon default)"
    )
    wallet_private_key: Optional[str] = None
    contract_address: Optional[str] = None
    
    # Data Product Configuration
    nft_metadata_uri_template: str = "https://ipfs.io/ipfs/{cid}"
    auction_interval_minutes: int = 15
    min_data_value_threshold: float = 0.01  # Minimum $ value to package
    
    # Health Monitoring
    vitals_poll_interval: int = 30  # seconds
    emotion_sample_rate: float = 0.1  # 10% sampling
    
    # Revenue Routing
    auto_pay_threshold_usd: float = 50.0
    api_creditor_wallet: Optional[str] = None
    
    # Adversarial Chaos Certification
    chaos_seal_salt: str = Field(
        default=os.getenv("CHAOS_SEAL_SALT", "default-chaos-salt"),
        description="Cryptographic salt for chaos seal generation"
    )
    
    # Logging Configuration
    log_level: str = "INFO"
    enable_telemetry: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        frozen = True  # Immutable config prevents runtime modifications
    
    @validator("firebase_credential_path")
    def validate_firebase_credential(cls, v: str) -> str:
        """Ensure Firebase credentials exist before initialization"""
        path = Path(v)
        if not path.exists():
            raise FileNotFoundError(
                f"Firebase credential file not found at: {v}. "
                f"Please download from Firebase Console and place at {path.absolute
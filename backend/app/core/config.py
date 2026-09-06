from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "NETRA-X"
    APP_FULL_NAME: str = "Network Evolution, Threat Recognition & Attack Forecasting Intelligence System"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/netrax"
    VALKEY_URL: str = "valkey://localhost:6379"
    SECRET_KEY: str = "supersecretkey_change_in_production"
    
    FEATURE_ZEEK: bool = True
    FEATURE_SURICATA: bool = True
    FEATURE_ARKIME: bool = False
    FEATURE_HONEYPOT: bool = True
    FEATURE_EBPF: bool = False
    FEATURE_GNN: bool = True
    FEATURE_LLM: bool = False
    FEATURE_NETBOX: bool = False
    FEATURE_KUBERNETES: bool = False
    FEATURE_THREAT_INTEL: bool = True
    FEATURE_IPFIX: bool = False
    
    PCAP_STORAGE_PATH: str = "/data/pcaps"
    EVIDENCE_PATH: str = "/data/evidence"
    CAPTURE_INTERFACE: str = "eth0"
    
    PERFORMANCE_PROFILE: str = "STANDARD"  # LIGHT, STANDARD, FORENSIC
    
    RETENTION_DAYS_EVENTS: int = 7
    RETENTION_DAYS_FLOWS: int = 30
    RETENTION_DAYS_PCAP: int = 3
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

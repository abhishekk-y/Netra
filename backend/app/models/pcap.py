from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class PCAPIndex(Base):
    __tablename__ = "pcap_indices"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    file_path: Mapped[str] = mapped_column(String)
    
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    
    file_size_bytes: Mapped[int] = mapped_column(Integer)
    packet_count: Mapped[int] = mapped_column(Integer)
    sha256_hash: Mapped[str] = mapped_column(String)
    
    sensor_id: Mapped[str] = mapped_column(String, index=True)

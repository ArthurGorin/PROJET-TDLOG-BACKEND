from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

# ==========================
# ÉVÉNEMENTS
# ==========================

class EventBase(BaseModel):
    name: str
    description: Optional[str] = None
    date: datetime
    location: str

class EventCreate(EventBase):
    """Données reçues pour créer un event"""
    pass

class EventOut(EventBase):
    """Données renvoyées au frontend"""
    id: int

    class Config:
        orm_mode = True  # permet de retourner des objets SQLAlchemy


# ==========================
# TICKETS
# ==========================

class TicketCreate(BaseModel):
    user_email: EmailStr
    user_name: str

class TicketsBulkCreate(BaseModel):
    attendees: List[TicketCreate]

class TicketOut(BaseModel):
    id: int
    event_id: int
    user_email: EmailStr
    user_name: str
    status: str
    scanned_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ScanRequest(BaseModel):
    token: str


class ScanResult(BaseModel):
    valid: bool          # True si le ticket est accepté
    reason: Optional[str] = None  # ex: "ticket_not_found", "already_scanned"
    user_email: Optional[EmailStr] = None
    user_name: Optional[str] = None
    event_id: Optional[int] = None
    status: Optional[str] = None   # UNUSED / SCANNED / CANCELED etc.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/scan", tags=["scan"])


@router.post("/", response_model=schemas.ScanResult)
def scan_ticket(
    payload: schemas.ScanRequest,
    db: Session = Depends(get_db),
):
    token = payload.token

    # On cherche le ticket qui correspond au token
    ticket = (
        db.query(models.Ticket)
        .filter(models.Ticket.qr_code_token == token)
        .first()
    )

    if ticket is None:
        # Aucun ticket ne correspond à ce token
        return schemas.ScanResult(
            valid=False,
            reason="ticket_not_found",
        )

    # Si déjà scanné
    if ticket.status == "SCANNED":
        return schemas.ScanResult(
            valid=False,
            reason="already_scanned",
            user_email=ticket.user_email,
            user_name=ticket.user_name,
            event_id=ticket.event_id,
            status=ticket.status,
        )

    # Si dans un autre état que UNUSED (ex: CANCELED)
    if ticket.status != "UNUSED":
        return schemas.ScanResult(
            valid=False,
            reason="invalid_status",
            user_email=ticket.user_email,
            user_name=ticket.user_name,
            event_id=ticket.event_id,
            status=ticket.status,
        )

    # 4) Ticket valide : on le marque comme scanné
    ticket.status = "SCANNED"
    ticket.scanned_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)

    return schemas.ScanResult(
        valid=True,
        reason=None,
        user_email=ticket.user_email,
        user_name=ticket.user_name,
        event_id=ticket.event_id,
        status=ticket.status,
    )


# On renvoie tout brut pour debug et voir les qr-code
@router.get("/debug_raw", tags=["tickets-debug"])
def list_raw_tickets(
    event_id: int,
    db: Session = Depends(get_db),
):
    tickets = db.query(models.Ticket).filter(models.Ticket.event_id == event_id).all()
    return [
        {
            "id": t.id,
            "user_email": t.user_email,
            "user_name": t.user_name,
            "qr_code_token": t.qr_code_token,
            "status": t.status,
            "scanned_at": t.scanned_at,
        }
        for t in tickets
    ]

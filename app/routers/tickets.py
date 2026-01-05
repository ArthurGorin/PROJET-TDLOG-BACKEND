from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import secrets

from app.db import get_db
from app import models, schemas


router = APIRouter(prefix="/events/{event_id}/tickets", tags=["tickets"])

#les deux fonctions de créations ne servent pas dans le front end, c'est si jamais on veut créer des tickets indépendamment d'un participants
def generate_ticket_token() -> str:
    """Génère un token aléatoire pour le ticket (ce sera ce qu'on mettra dans le QR code)"""
    return secrets.token_urlsafe(16)


@router.post("/", response_model=schemas.TicketOut)
def create_ticket(
    event_id: int,
    data: schemas.TicketCreate,
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")

    ticket = models.Ticket(
        event_id=event_id,
        user_email=data.user_email,
        user_name=data.user_name,
        qr_code_token=generate_ticket_token(),
        status="UNUSED",
        scanned_at=None,
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/bulk", response_model=list[schemas.TicketOut])
def create_tickets_bulk(
    event_id: int,
    data: schemas.TicketsBulkCreate,
    db: Session = Depends(get_db),
):
    # Vérifier que l'event existe
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")

    created_tickets: list[models.Ticket] = []

    for attendee in data.attendees:
        ticket = models.Ticket(
            event_id=event_id,
            user_email=attendee.user_email,
            user_name=attendee.user_name,
            qr_code_token=generate_ticket_token(),
            status="UNUSED",
            scanned_at=None,
        )
        db.add(ticket)
        created_tickets.append(ticket)

    db.commit()

    # Refresh pour avoir les IDs
    for t in created_tickets:
        db.refresh(t)

    return created_tickets


@router.get("/", response_model=list[schemas.TicketOut])
def list_tickets_for_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")

    tickets = db.query(models.Ticket).filter(models.Ticket.event_id == event_id).all()
    return tickets

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=schemas.EventOut)
def create_event(event_in: schemas.EventCreate, db: Session = Depends(get_db)):
    event = models.Event(
        name=event_in.name,
        description=event_in.description,
        date=event_in.date,
        location=event_in.location,
        created_by_id=None,  # on branchera l'auth plus tard
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/", response_model=list[schemas.EventOut])
def list_events(db: Session = Depends(get_db)):
    events = db.query(models.Event).all()
    return events


@router.get("/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")
    return event

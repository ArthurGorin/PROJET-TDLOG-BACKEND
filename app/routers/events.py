from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/events", tags=["events"])


def _check_user_is_event_owner(
    event_id: int,
    current_user: models.User,
    db: Session,
):
    """Authorize only superadmins or event owners (role OWNER)."""
    if current_user.is_superadmin:
        return

    rel = (
        db.query(models.EventAdmin)
        .filter(
          models.EventAdmin.event_id == event_id,
          models.EventAdmin.user_id == current_user.id,
          models.EventAdmin.role == "OWNER",
        )
        .first()
    )
    if rel is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès refusé : admin de l'événement requis",
        )


@router.post("/", response_model=schemas.EventOut)
def create_event(
    event_in: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    event = models.Event(
        name=event_in.name,
        description=event_in.description,
        date=event_in.date,
        location=event_in.location,
        created_by_id=current_user.id,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # le créateur devient OWNER
    rel = models.EventAdmin(
        event_id=event.id,
        user_id=current_user.id,
        role="OWNER",
    )
    db.add(rel)
    db.commit()

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


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")

    _check_user_is_event_owner(event_id, current_user, db)

    db.delete(event)
    db.commit()


@router.put("/{event_id}", response_model=schemas.EventOut)
def update_event(
    event_id: int,
    event_in: schemas.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")

    _check_user_is_event_owner(event_id, current_user, db)

    event.name = event_in.name
    event.description = event_in.description
    event.date = event_in.date
    event.location = event_in.location

    db.commit()
    db.refresh(event)
    return event

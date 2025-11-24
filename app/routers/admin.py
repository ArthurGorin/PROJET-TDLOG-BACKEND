from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app import models, schemas
from app.deps import get_current_user

router = APIRouter(prefix="/events/{event_id}/admins", tags=["admins"])


def _check_user_can_manage_event(
    event: models.Event,
    current_user: models.User,
    db: Session,
):
    # superadmin = full power
    if current_user.is_superadmin:
        return

    # est-ce que current_user est OWNER de l'event ?
    rel = (
        db.query(models.EventAdmin)
        .filter(
            models.EventAdmin.event_id == event.id,
            models.EventAdmin.user_id == current_user.id,
            models.EventAdmin.role == "OWNER",
        )
        .first()
    )
    if rel is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu n'es pas owner de cet event",
        )


@router.post("/")
def add_admin_to_event(
    event_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    body attendu :
    {
      "user_email": "newadmin@example.com",
      "role": "SCANNER_ONLY" ou "OWNER"
    }
    """
    user_email = body.get("user_email")
    role = body.get("role", "SCANNER_ONLY")

    if not user_email:
        raise HTTPException(status_code=400, detail="user_email manquant")

    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")

    _check_user_can_manage_event(event, current_user, db)

    user = db.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # éviter les doublons
    existing = (
        db.query(models.EventAdmin)
        .filter(
            models.EventAdmin.event_id == event_id,
            models.EventAdmin.user_id == user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Cet utilisateur est déjà admin de cet event")

    rel = models.EventAdmin(
        event_id=event_id,
        user_id=user.id,
        role=role,
    )
    db.add(rel)
    db.commit()
    db.refresh(rel)

    return {
        "message": "Admin ajouté",
        "event_id": event_id,
        "user_id": user.id,
        "role": role,
    }


@router.get("/")
def list_event_admins(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event non trouvé")

    _check_user_can_manage_event(event, current_user, db)

    rels = (
        db.query(models.EventAdmin)
        .filter(models.EventAdmin.event_id == event_id)
        .all()
    )

    result = []
    for rel in rels:
        user = db.query(models.User).filter(models.User.id == rel.user_id).first()
        result.append(
            {
                "user_id": user.id,
                "user_email": user.email,
                "user_name": user.name,
                "role": rel.role,
            }
        )

    return result


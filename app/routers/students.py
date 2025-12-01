# app/routers/students.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from .. import models, schemas
from ..db import get_db
import csv

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

@router.get("/", response_model=list[schemas.Student])
def list_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@router.post("/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # éviter les doublons d’email
    existing = db.query(models.Student).filter(
        models.Student.email == student.email
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà enregistré")

    db_student = models.Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@router.post("/import-csv")
async def import_students_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    CSV avec au moins les colonnes : nom, prenom, email
    (adaptable selon ton fichier)
    """
    content = await file.read()
    lines = content.decode("utf-8").splitlines()

    reader = csv.DictReader(lines, delimiter=";")  # ou "," selon ton fichier

    inserted = 0
    for row in reader:
        # adapte les noms de colonnes à ton CSV
        first_name = row["prenom"].strip()
        last_name = row["nom"].strip()
        email = row["email"].strip()

        # on ignore si déjà présent
        existing = db.query(models.Student).filter(
            models.Student.email == email
        ).first()
        if existing:
            continue

        student = models.Student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_external=False,
        )
        db.add(student)
        inserted += 1

    db.commit()
    return {"inserted": inserted}

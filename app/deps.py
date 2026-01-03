from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db import get_db
from app import models, schemas
from app.security import ALGORITHM, SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") #l'authentificatin ce fait par un token qui vient de post /auth/login


def get_user_by_id(user_id: int, db: Session) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


async def get_current_user(
    token: str = Depends(oauth2_scheme), #recupere le token depuis le header de la requete http
    db: Session = Depends(get_db), #ouvre une session db
) -> models.User:
    credentials_exception = HTTPException( #erreur standard si le token est invalide
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) #decodage du jwt
        raw_user_id = payload.get("sub") 
        if raw_user_id is None:
            raise credentials_exception
        try:
            user_id = int(raw_user_id) #on essaye de récupérer l'id
        except (TypeError, ValueError):
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(user_id=user_id, db=db) #on récupère l'utilisateur
    if user is None:
        raise credentials_exception

    return user #on renvoie l'utilisateur

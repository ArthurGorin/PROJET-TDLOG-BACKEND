from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = 'sqlite:///./app.db' #la db est stocké à la racine du back dans app.db
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False}) #moteur sql
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #une conversation avec la DB, chaque requete http aura sa propre session
Base = declarative_base() #classe mère de toutes les tables

def get_db(): #dépendance fast api : ouvre une session db la donne à la route puis la ferme automatiquement
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

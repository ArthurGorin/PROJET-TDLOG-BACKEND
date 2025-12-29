from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 

from .routers import auth, events, tickets, scan, admin, students, participants
from .db import Base, engine
from .initial_superadmin import ensure_initial_superadmin

# Création des tables au démarrage
Base.metadata.create_all(bind=engine)

#garantit qu'au moins un admin existe (si nouvelle db)
ensure_initial_superadmin() 

#création de l'app centrale
app = FastAPI(title="TD-LOG API", version="0.1.0")

#route de base Quand on lance le backend
@app.get("/")
def root():
    return {"message": "Backend TDLOG running"}

#petit test initial
@app.get("/health")
def health():
    return {"status": "ok"}

#autorise le frontend à appeler le backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en dev : on autorise tout, on durcira plus tard si besoin
    allow_credentials=True,
    allow_methods=["*"],   # <- très important pour accepter OPTIONS
    allow_headers=["*"],
)

#branchement des routes
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(scan.router)
app.include_router(admin.router)
app.include_router(students.router)
app.include_router(participants.router)

from fastapi import FastAPI
from .routers import auth, events, tickets, scan, admin
from .db import Base, engine

# Création des tables au démarrage (simple pour dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TD-LOG API", version="0.1.0")

# 1) Ping simple pour savoir si le serveur est vivant
@app.get("/health")
def health():
    return {"status": "ok"}

# 2) Exemple de route "hello"
@app.get("/hello")
def hello(name: str = "world"):
    return {"message": f"Hello {name}!"}

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(scan.router)
app.include_router(admin.router)

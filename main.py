# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="TD-LOG API", version="0.1.0")

# 1) Ping simple pour savoir si le serveur est vivant
@app.get("/health")
def health():
    return {"status": "ok"}

# 2) Exemple de route "hello"
@app.get("/hello")
def hello(name: str = "world"):
    return {"message": f"Hello {name}!"}

# 3) Mini-API tickets (mémoire = reset à chaque démarrage)
class TicketIn(BaseModel):
    code: str

class TicketOut(BaseModel):
    id: int
    code: str
    valid: bool

TICKETS = []   # stock en RAM (pour débuter)

@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(t: TicketIn):
    new = {"id": len(TICKETS) + 1, "code": t.code, "valid": True}
    TICKETS.append(new)
    return new

@app.get("/tickets")
def list_tickets():
    return TICKETS
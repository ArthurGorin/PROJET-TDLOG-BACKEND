from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .db import Base

class User(Base): #utilisateurs de l'app
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    is_superadmin = Column(Boolean, default=False)

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    date = Column(DateTime)
    location = Column(String)
    created_by_id = Column(Integer, ForeignKey('users.id'))
    created_by = relationship('User')

class EventAdmin(Base): #table de liaisons un event peut avoir plusieurs admins et un admin peut créer plusieurs events
    __tablename__ = 'event_admins'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    role = Column(String)

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    user_email = Column(String)
    user_name = Column(String)
    qr_code_token = Column(String, unique=True, index=True)
    status = Column(String, default='UNUSED')
    scanned_at = Column(DateTime)

class Student(Base): #annuaire
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_external = Column(Boolean, default=False)


class Participant(Base): #participants d'un évènement
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    promo = Column(String, nullable=True)
    email = Column(String, nullable=True)
    tarif = Column(String, nullable=True)
    qr_code = Column(String, unique=True, index=True, nullable=False)
    event = relationship("Event", backref="participants") #permet de faire event.participants et participant.event

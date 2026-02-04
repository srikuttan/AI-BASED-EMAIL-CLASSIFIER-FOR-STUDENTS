from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    sent_emails = relationship("Email", foreign_keys="[Email.sender_id]", back_populates="sender")
    received_emails = relationship("Email", foreign_keys="[Email.recipient_id]", back_populates="recipient")

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String)
    body = Column(String)
    category = Column(String) # Assignments, Notices, Personal, Spam
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_emails")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_emails")

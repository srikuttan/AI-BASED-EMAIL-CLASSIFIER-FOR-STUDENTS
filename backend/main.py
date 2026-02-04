from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, database, auth, classifier
from .database import engine, get_db
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import timedelta

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS config
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
# Dependency imported from database.py now

# Pydantic Schemas
class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class EmailCreate(BaseModel):
    recipient_email: str
    subject: str
    body: str

class EmailResponse(BaseModel):
    id: int
    subject: str
    body: str
    category: str
    sender_email: str
    timestamp: str

    model_config = ConfigDict(from_attributes=True)

# Routes

@app.post("/auth/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pass = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = auth.create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = auth.authenticate_user(db, user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/emails/send")
def send_email(email: EmailCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipient = auth.get_user(db, email=email.recipient_email)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Predict category
    category = classifier.classifier.predict(email.subject, email.body)
    
    new_email = models.Email(
        sender_id=current_user.id,
        recipient_id=recipient.id,
        subject=email.subject,
        body=email.body,
        category=category
    )
    db.add(new_email)
    db.commit()
    
    return {"message": "Email sent successfully", "category": category}

@app.get("/emails/inbox")
def get_inbox(db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    emails = db.query(models.Email).filter(models.Email.recipient == current_user).order_by(models.Email.timestamp.desc()).all()
    
    return [
        {
            "id": e.id,
            "subject": e.subject,
            "body": e.body,
            "category": e.category,
            "sender_email": e.sender.email,
            "timestamp": e.timestamp.isoformat()
        }
        for e in emails
    ]

# Serve Static Files
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Create static directory if it doesn't exist
if not os.path.exists("static"):
    os.makedirs("static")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    print("Starting server... Open this link in your browser: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)

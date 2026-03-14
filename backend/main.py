import os
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, database, auth, classifier
from .database import engine, get_db
from pydantic import BaseModel, ConfigDict
from pathlib import Path

# Feature flag: initial value from env; can be changed at runtime via API
_initial_classification = os.getenv("ENABLE_EMAIL_CLASSIFICATION", "true").lower() in ("true", "1", "yes")
runtime_config = {"enable_email_classification": _initial_classification}
DEFAULT_CATEGORY_WHEN_DISABLED = "Personal"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("ENABLE_EMAIL_CLASSIFICATION = %s", runtime_config["enable_email_classification"])

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

class EmailUpdateCategory(BaseModel):
    category: str

class ClassificationConfigUpdate(BaseModel):
    enabled: bool

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

@app.get("/config/classification")
def get_classification_config(current_user: models.User = Depends(auth.get_current_user)):
    return {"enabled": runtime_config["enable_email_classification"]}

@app.patch("/config/classification")
def update_classification_config(
    payload: ClassificationConfigUpdate,
    current_user: models.User = Depends(auth.get_current_user),
):
    runtime_config["enable_email_classification"] = payload.enabled
    logger.info("ENABLE_EMAIL_CLASSIFICATION set to %s via API", payload.enabled)
    return {"enabled": runtime_config["enable_email_classification"]}

@app.post("/emails/send")
def send_email(email: EmailCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    recipient = auth.get_user(db, email=email.recipient_email)
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Predict category (or use default when classification is disabled)
    if runtime_config["enable_email_classification"]:
        category = classifier.classifier.predict(email.subject, email.body)
    else:
        category = DEFAULT_CATEGORY_WHEN_DISABLED

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

@app.patch("/emails/{email_id}/category")
def update_email_category(
    email_id: int,
    payload: EmailUpdateCategory,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    email = db.query(models.Email).filter(models.Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # Only allow the recipient to change the classification
    if email.recipient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to change this email")

    allowed_categories = ["Assignments", "Notices", "Personal", "Spam"]
    if payload.category not in allowed_categories:
        raise HTTPException(status_code=400, detail="Invalid category")

    email.category = payload.category
    db.commit()
    db.refresh(email)

    return {
        "id": email.id,
        "subject": email.subject,
        "body": email.body,
        "category": email.category,
        "sender_email": email.sender.email,
        "timestamp": email.timestamp.isoformat(),
    }

# Serve Static Files (paths relative to project root for any CWD)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

_BASE_DIR = Path(__file__).resolve().parent.parent
_STATIC_DIR = _BASE_DIR / "static"
if not _STATIC_DIR.exists():
    _STATIC_DIR.mkdir(parents=True)

app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    index_path = _STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Static files not found")
    return FileResponse(str(index_path))

if __name__ == "__main__":
    import uvicorn
    print("Starting server... Open this link in your browser: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)

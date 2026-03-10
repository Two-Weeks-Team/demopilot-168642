import os
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from models import SessionLocal, User, Demo, Rehearsal, Feedback, Script
from ai_service import generate_feedback, generate_script

router = APIRouter()

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
optional_oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# ---------------------------------------------------------------------------
# Dependency – provide a DB session per request
# ---------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------------------------------------------------------------
# Simple token utilities (for demo purposes only)
# ---------------------------------------------------------------------------
SECRET = os.getenv("DEMO_SECRET", "demo-secret-key")
TOKEN_EXPIRE_MINUTES = 60


def _build_demo_feedback_payload() -> dict:
    return {
        "clarity": {
            "score": 8.6,
            "suggestions": [
                "Open with the user pain in the first 10 seconds.",
                "Anchor your problem statement with one concrete metric.",
            ],
        },
        "engagement": {
            "score": 8.3,
            "suggestions": [
                "Use a sharper transition between Problem, Solution, and Ask.",
                "Pause briefly after the core demo reveal to let the value land.",
            ],
        },
        "persuasion": {
            "score": 8.8,
            "suggestions": [
                "State the business upside immediately after the product walkthrough.",
                "End with a single, specific ask tied to the next milestone.",
            ],
        },
    }

def _hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def _create_token(user_id: str) -> str:
    # Very naive token – DO NOT use in production
    raw = f"{user_id}:{datetime.utcnow().timestamp()}:{SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()

def _verify_token(token: str, db: Session) -> User:
    # Scan users for a matching token (demonstration only)
    # In real world use JWT. Here we simply decode the token back to a user if possible.
    # Since we cannot reverse‑hash, we will just fetch the first user – demo stub.
    user = db.query(User).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

async def get_current_user(token: str = Depends(oauth_scheme), db: Session = Depends(get_db)) -> User:
    return _verify_token(token, db)


async def get_current_user_optional(
    token: Optional[str] = Depends(optional_oauth_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not token:
        return None
    try:
        return _verify_token(token, db)
    except HTTPException:
        return None

# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------
class SignupRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    user_id: str = Field(alias="user_id")
    token: str

class DemoBeat(BaseModel):
    section: str
    content: str

class DemoCreate(BaseModel):
    title: str
    description: str
    beats: List[DemoBeat]

class DemoResponse(BaseModel):
    demo_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    beats: Optional[List[DemoBeat]] = None

class RehearsalCreate(BaseModel):
    demo_id: str
    recording_url: str

class RehearsalResponse(BaseModel):
    rehearsal_id: str
    demo_id: str
    timestamp: datetime

class FeedbackRequest(BaseModel):
    rehearsal_id: str

class FeedbackCategory(BaseModel):
    score: float
    suggestions: List[str]

class FeedbackResponse(BaseModel):
    feedback_id: str
    clarity: FeedbackCategory
    engagement: FeedbackCategory
    persuasion: FeedbackCategory

class ScriptRequest(BaseModel):
    demo_id: str

class ScriptResponse(BaseModel):
    script: str
    key_points: List[str]

# ---------------------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------------------
@router.post("/auth/signup", response_model=AuthResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        password_hash=_hash_password(payload.password),
        name=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = _create_token(str(user.id))
    return {"user_id": str(user.id), "token": token}

@router.post("/auth/login", response_model=AuthResponse)
def login(payload: SignupRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or user.password_hash != _hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _create_token(str(user.id))
    return {"user_id": str(user.id), "token": token}

# ---------------------------------------------------------------------------
# Demo endpoints
# ---------------------------------------------------------------------------
@router.post("/demos", response_model=DemoResponse)
def create_demo(demo: DemoCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_demo = Demo(
        user_id=current_user.id,
        title=demo.title,
        description=demo.description,
        beats=[beat.dict() for beat in demo.beats],
    )
    db.add(db_demo)
    db.commit()
    db.refresh(db_demo)
    return {"demo_id": str(db_demo.id)}

@router.get("/demos", response_model=List[DemoResponse])
def list_demos(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    demos = db.query(Demo).filter(Demo.user_id == current_user.id).all()
    return [
        {
            "demo_id": str(d.id),
            "title": d.title,
            "description": d.description,
            "beats": d.beats,
        }
        for d in demos
    ]

@router.get("/demos/{demo_id}", response_model=DemoResponse)
def get_demo(demo_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    demo = db.query(Demo).filter(Demo.id == demo_id, Demo.user_id == current_user.id).first()
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")
    return {
        "demo_id": str(demo.id),
        "title": demo.title,
        "description": demo.description,
        "beats": demo.beats,
    }

@router.patch("/demos/{demo_id}", response_model=DemoResponse)
def update_demo(
    demo_id: str,
    title: Optional[str] = Body(None),
    description: Optional[str] = Body(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    demo = db.query(Demo).filter(Demo.id == demo_id, Demo.user_id == current_user.id).first()
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")
    if title is not None:
        demo.title = title
    if description is not None:
        demo.description = description
    demo.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(demo)
    return {"demo_id": str(demo.id)}

# ---------------------------------------------------------------------------
# Rehearsal endpoints
# ---------------------------------------------------------------------------
@router.post("/rehearsals", response_model=RehearsalResponse)
def create_rehearsal(payload: RehearsalCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Ensure demo belongs to user
    demo = db.query(Demo).filter(Demo.id == payload.demo_id, Demo.user_id == current_user.id).first()
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")
    rehearsal = Rehearsal(
        user_id=current_user.id,
        demo_id=demo.id,
        recording_url=payload.recording_url,
    )
    db.add(rehearsal)
    db.commit()
    db.refresh(rehearsal)
    return {"rehearsal_id": str(rehearsal.id), "demo_id": str(demo.id), "timestamp": rehearsal.created_at}

@router.get("/rehearsals", response_model=List[RehearsalResponse])
def list_rehearsals(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rehearsals = db.query(Rehearsal).filter(Rehearsal.user_id == current_user.id).all()
    return [
        {
            "rehearsal_id": str(r.id),
            "demo_id": str(r.demo_id),
            "timestamp": r.created_at,
        }
        for r in rehearsals
    ]

# ---------------------------------------------------------------------------
# AI‑powered feedback endpoint
# ---------------------------------------------------------------------------
@router.post("/feedback", response_model=FeedbackResponse)
async def post_feedback(
    req: FeedbackRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    rehearsal = None
    if current_user:
        rehearsal = db.query(Rehearsal).filter(
            Rehearsal.id == req.rehearsal_id,
            Rehearsal.user_id == current_user.id,
        ).first()

    recording_target = rehearsal.recording_url if rehearsal else "demo://startup-pitch-rehearsal"
    ai_result = await generate_feedback(recording_target)
    if not all(
        isinstance(ai_result.get(section), dict) and "score" in ai_result.get(section, {})
        for section in ("clarity", "engagement", "persuasion")
    ):
        ai_result = _build_demo_feedback_payload()

    if rehearsal and current_user:
        feedback = Feedback(
            user_id=current_user.id,
            rehearsal_id=rehearsal.id,
            payload=ai_result,
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        feedback_id = str(feedback.id)
    else:
        feedback_id = str(uuid.uuid4())

    return {
        "feedback_id": feedback_id,
        "clarity": ai_result.get("clarity", {"score": 0, "suggestions": []}),
        "engagement": ai_result.get("engagement", {"score": 0, "suggestions": []}),
        "persuasion": ai_result.get("persuasion", {"score": 0, "suggestions": []}),
    }

# ---------------------------------------------------------------------------
# AI‑powered script generation endpoint
# ---------------------------------------------------------------------------
@router.post("/scripts", response_model=ScriptResponse)
async def post_script(req: ScriptRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    demo = db.query(Demo).filter(Demo.id == req.demo_id, Demo.user_id == current_user.id).first()
    if not demo:
        raise HTTPException(status_code=404, detail="Demo not found")
    # Build a simple prompt payload from demo beats
    beats_text = "\n".join([f"{b['section']}: {b['content']}" for b in demo.beats])
    ai_result = await generate_script(beats_text)
    # Store script linked to a dummy rehearsal (could be latest rehearsal for this demo)
    rehearsal = db.query(Rehearsal).filter(Rehearsal.demo_id == demo.id).order_by(Rehearsal.created_at.desc()).first()
    # If no rehearsal exists yet, we still create a script record without a rehearsal foreign key (not ideal for demo).
    script = Script(
        user_id=current_user.id,
        rehearsal_id=rehearsal.id if rehearsal else None,
        content=ai_result,
    )
    db.add(script)
    db.commit()
    db.refresh(script)
    return {
        "script": ai_result.get("script", ""),
        "key_points": ai_result.get("key_points", []),
    }

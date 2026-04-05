import random
import string
import time
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store: code -> session dict
sessions: dict = {}
SESSION_TTL = 600  # 10 minutes


def _cleanup():
    now = time.time()
    expired = [k for k, v in sessions.items() if now - v["created"] > SESSION_TTL]
    for k in expired:
        del sessions[k]


def _get_session(code: str):
    session = sessions.get(code.upper())
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return session


class SDPPayload(BaseModel):
    sdp: str
    type: str


class ICECandidate(BaseModel):
    candidate: str
    sdpMid: Optional[str] = None
    sdpMLineIndex: Optional[int] = None


@app.get("/")
def root():
    return {"message": "BridgeBeam signaling server"}


@app.post("/api/session")
def create_session():
    _cleanup()
    for _ in range(20):
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if code not in sessions:
            sessions[code] = {
                "created": time.time(),
                "offer": None,
                "answer": None,
                "sender_ice": [],
                "receiver_ice": [],
            }
            return {"code": code}
    raise HTTPException(status_code=503, detail="Could not generate unique code")


@app.put("/api/session/{code}/offer")
def set_offer(code: str, payload: SDPPayload):
    session = _get_session(code)
    session["offer"] = {"sdp": payload.sdp, "type": payload.type}
    return {"ok": True}


@app.get("/api/session/{code}/offer")
def get_offer(code: str):
    session = _get_session(code)
    if not session["offer"]:
        raise HTTPException(status_code=204, detail="No offer yet")
    return session["offer"]


@app.put("/api/session/{code}/answer")
def set_answer(code: str, payload: SDPPayload):
    session = _get_session(code)
    session["answer"] = {"sdp": payload.sdp, "type": payload.type}
    return {"ok": True}


@app.get("/api/session/{code}/answer")
def get_answer(code: str):
    session = _get_session(code)
    if not session["answer"]:
        raise HTTPException(status_code=204, detail="No answer yet")
    return session["answer"]


@app.post("/api/session/{code}/ice/{role}")
def add_ice(code: str, role: str, candidate: ICECandidate):
    if role not in ("sender", "receiver"):
        raise HTTPException(status_code=400, detail="role must be 'sender' or 'receiver'")
    session = _get_session(code)
    session[f"{role}_ice"].append({
        "candidate": candidate.candidate,
        "sdpMid": candidate.sdpMid,
        "sdpMLineIndex": candidate.sdpMLineIndex,
    })
    return {"ok": True}


@app.get("/api/session/{code}/ice/{role}")
def get_ice(code: str, role: str, after: int = 0):
    if role not in ("sender", "receiver"):
        raise HTTPException(status_code=400, detail="role must be 'sender' or 'receiver'")
    session = _get_session(code)
    candidates = session[f"{role}_ice"][after:]
    return {"candidates": candidates, "total": len(session[f"{role}_ice"])}

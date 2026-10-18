import os
from collections import defaultdict

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow browser-based cross-origin requests from the assignment page.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.environ.get("API_KEY", "")
EMAIL = os.environ.get("EMAIL", "")


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: list[Event]


@app.post("/analytics")
def analytics(
    request: AnalyticsRequest,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    # Missing or incorrect keys must receive HTTP 401.
    if not API_KEY or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    total_events = len(request.events)
    unique_users = {event.user for event in request.events}
    positive_revenue_by_user = defaultdict(float)

    for event in request.events:
        if event.amount > 0:
            positive_revenue_by_user[event.user] += event.amount

    revenue = sum(positive_revenue_by_user.values())
    top_user = (
        max(positive_revenue_by_user, key=positive_revenue_by_user.get)
        if positive_revenue_by_user
        else None
    )

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": len(unique_users),
        "revenue": revenue,
        "top_user": top_user,
    }


@app.get("/")
def health():
    return {"status": "ok"}

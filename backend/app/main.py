from fastapi import FastAPI
from backend.app.api.v1.router import api_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.contributors import router as contributors_router
from backend.app.db.postgres import engine, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

app.include_router(api_router)
app.include_router(dashboard_router)
app.include_router(contributors_router)

@app.get("/")
def root():
    return {"message": "OEG running 🚀"}
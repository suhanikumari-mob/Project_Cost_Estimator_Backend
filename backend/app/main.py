from fastapi import FastAPI
from app.router.estimation import router as estimate_router

app = FastAPI(
    title="Cost Estimation API"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000","https://project-cost-estimator-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(estimate_router)

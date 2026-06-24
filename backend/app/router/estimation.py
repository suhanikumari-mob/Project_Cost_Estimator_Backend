from fastapi import UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi import APIRouter, HTTPException, Depends
from app.services.document_service import load_document
from app.services.excel_service import generate_xls
from app.services.pdf_service import generator_pdf
from app.services.question_service import question_generator
from app.services.estimate_injson_service import estimator_json
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import verify_token, create_access_token
from datetime import UTC, datetime, timedelta
from app.repositories.user_repository import (
    check_emailpass, register_user, save_project,
    get_next_threadid, get_threadids, get_project_response
)
import tempfile
import zipfile
import json
import regex as re
from typing import Optional

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    return payload

router = APIRouter(tags=["Estimation"])


@router.post("/register/")
def register(Name: str, Email: str, Password: str):
    return {"Message": register_user(Name, Email, Password)}


@router.post("/login")
def login(Email: str, Password: str):
    r = check_emailpass(Email, Password)
    if not r["success"]:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "email": r["email"],
        "userid": r["userid"]
    })
    return {"token": token}


@router.post("/estimate/both")
async def download_zip(query: str = Form(""), requirement: UploadFile = File(...), p=Depends(get_current_user)):
    email  = p["email"]
    userid = p["userid"]

    requirements_bytes = await requirement.read()
    docs   = load_document(requirements_bytes)
    answer = question_generator(docs, query)

    print(f"ANSWER FROM QUESTIONS: {answer}")

    response = estimator_json(docs, answer)

    print(f"RESPONSE FROM LLM: {repr(response[:300])}")

    if not response or not response.strip():
        raise HTTPException(status_code=500, detail="LLM returned empty response")

    try:
        response_dict = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"JSON PARSE ERROR: {e}")
        print(f"RAW CONTENT: {repr(response)}")
        raise HTTPException(status_code=500, detail=f"LLM response is not valid JSON: {str(e)}")

    project_name = response_dict.get("title", "Untitled Project")
    thread_id    = get_next_threadid(userid)

    # save response_json so history re-download works without re-running LLM
    save_project(userid, email, thread_id, project_name, response)

    pdf_path   = generator_pdf(response)
    excel_path = generate_xls(response, "cost_estimation_report.xlsx")

    zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(zip_file.name, "w") as zipf:
        zipf.write(pdf_path,   arcname="cost_estimation_report.pdf")
        zipf.write(excel_path, arcname="cost_estimation_report.xlsx")

    return FileResponse(zip_file.name, media_type="application/zip", filename="cost_estimation_report.zip")


@router.post("/estimate/regenerate/{thread_id}")
async def regenerate_estimate(thread_id: int, p=Depends(get_current_user)):
    userid   = p["userid"]
    response = get_project_response(userid, thread_id)  # fetch saved JSON — no LLM call

    if not response:
        raise HTTPException(status_code=404, detail="Project not found")

    pdf_path   = generator_pdf(response)
    excel_path = generate_xls(response, "cost_estimation_report.xlsx")

    zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(zip_file.name, "w") as zipf:
        zipf.write(pdf_path,   arcname="cost_estimation_report.pdf")
        zipf.write(excel_path, arcname="cost_estimation_report.xlsx")

    return FileResponse(zip_file.name, media_type="application/zip", filename="cost_estimation_report.zip")


@router.get("/projects")
def get_projects(p=Depends(get_current_user)):
    userid = p["userid"]
    return get_threadids(userid)


@router.post("/estimate/questions")
async def get_questions(
    query: str = Form(""),
    requirement: UploadFile = File(...),
    p=Depends(get_current_user)
):
    requirements_bytes = await requirement.read()
    docs = load_document(requirements_bytes)
    questions = question_generator(docs, query)
    return {"questions": questions}

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from s3_scanner import scan_s3_bucket
from pydantic import BaseModel
from typing import List
import shutil
import os

# --- Custom Modules ---
from analyzer import scan_text_for_pii 
from report_engine import generate_pdf_bytes 
from db_scanner import scan_live_database
# IMPORT THE HISTORY MODULE
from history_db import save_scan_result, get_recent_scans 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class LeakDetail(BaseModel):
    type: str
    value_masked: str
    line: str 

class ReportRequest(BaseModel):
    filename: str
    findings: List[LeakDetail]

class DBConnectionRequest(BaseModel):
    connection_string: str

class S3ScanRequest(BaseModel):
    access_key: str
    secret_key: str
    bucket_name: str
    region: str

# --- Endpoints ---

@app.get("/")
def home():
    return {"status": "online", "message": "DPDP Scanner API is ready"}

@app.get("/history/")
def get_history():
    """Fetches the list of past scans for the dashboard"""
    return get_recent_scans()

@app.post("/scan-file/")
async def scan_file(file: UploadFile = File(...)):
    if not (file.filename.endswith('.csv') or file.filename.endswith('.sql') or file.filename.endswith('.txt')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV, SQL, or TXT allowed.")

    temp_filename = f"temp_{file.filename}"
    findings = []
    
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        with open(temp_filename, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                line_leaks = scan_text_for_pii(line, line_number=str(i+1))
                findings.extend(line_leaks)

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

    # --- SAVE TO HISTORY DB ---
    risk_status = "HIGH" if len(findings) > 0 else "LOW"
    save_scan_result(file.filename, len(findings), risk_status)

    return {
        "filename": file.filename,
        "total_leaks": len(findings),
        "risk_score": risk_status,
        "compliance_status": "NON_COMPLIANT" if findings else "COMPLIANT",
        "details": findings
    }

@app.post("/scan-database/")
async def scan_database(request: DBConnectionRequest):
    print(f"[*] Received connection string: {request.connection_string}")
    
    findings = scan_live_database(request.connection_string)
    
    if isinstance(findings, dict) and "error" in findings:
         raise HTTPException(status_code=400, detail=findings["error"])

    # --- SAVE TO HISTORY DB ---
    risk_status = "HIGH" if len(findings) > 0 else "LOW"
    save_scan_result("Live Database Scan", len(findings), risk_status)

    return {
        "filename": "Live Database Scan",
        "total_leaks": len(findings),
        "risk_score": risk_status,
        "compliance_status": "NON_COMPLIANT" if findings else "COMPLIANT",
        "details": findings
    }

@app.post("/generate-pdf/")
async def generate_pdf(request: ReportRequest):
    pdf_buffer = generate_pdf_bytes(request.filename, request.findings)
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Audit_Report_{request.filename}.pdf"}
    )
@app.post("/scan-s3/")
async def scan_s3(request: S3ScanRequest):
    """
    FEATURE 4: AWS S3 Cloud Scanner
    """
    print(f"[*] Starting S3 Scan for bucket: {request.bucket_name}")
    
    findings = scan_s3_bucket(
        request.access_key, 
        request.secret_key, 
        request.bucket_name, 
        request.region
    )
    
    # Error Handling
    if isinstance(findings, dict) and "error" in findings:
         raise HTTPException(status_code=400, detail=findings["error"])

    # Save to History
    risk_status = "HIGH" if len(findings) > 0 else "LOW"
    save_scan_result(f"S3 Bucket: {request.bucket_name}", len(findings), risk_status)

    return {
        "filename": f"AWS S3: {request.bucket_name}",
        "total_leaks": len(findings),
        "risk_score": risk_status,
        "compliance_status": "NON_COMPLIANT" if findings else "COMPLIANT",
        "details": findings
    }
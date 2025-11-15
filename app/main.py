from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.schemas import EmailTextRequest, EmailAnalysisResponse
from app.services.ai_client import classify_and_reply
from app.services.text_extractor import extract_text_from_txt, extract_text_from_pdf


app = FastAPI(
    title="EmailSmart – Email Classifier",
    description="API to classify emails (Productive / Non-productive) and suggest automatic replies.",
    version="0.1.0",
)

# HTML templates (landing page)
templates = Jinja2Templates(directory="templates")

# Static assets (CSS / JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS (open for local dev; restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def home(request: Request):
    """
    Render the HTML landing page with the classifier UI.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
def health_check():
    """
    Simple health check endpoint for monitoring.
    """
    return {"status": "ok"}


@app.post("/analyze-text", response_model=EmailAnalysisResponse)
def analyze_text(payload: EmailTextRequest):
    """
    Analyze raw email text and return classification and suggested reply.
    """
    result = classify_and_reply(payload.text)
    return result


@app.post("/analyze-file", response_model=EmailAnalysisResponse)
async def analyze_file(file: UploadFile = File(...)):
    """
    Analyze a .txt or .pdf file: extract text, classify, and suggest a reply.
    """
    filename = (file.filename or "").lower()
    content_type = (file.content_type or "").lower()

    if filename.endswith(".txt") or "text/plain" in content_type:
        text = extract_text_from_txt(file.file)
    elif filename.endswith(".pdf") or "pdf" in content_type:
        text = extract_text_from_pdf(file.file)
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a .txt or .pdf file.",
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the uploaded file.",
        )

    result = classify_and_reply(text)
    return result

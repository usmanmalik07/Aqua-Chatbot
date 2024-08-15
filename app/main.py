from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io
import openai
from dotenv import load_dotenv
import os
from .database import connect_to_mongo, get_database
from .openai_utils import generate_questions, evaluate_responses
from fastapi import HTTPException

load_dotenv()

app = FastAPI()

# Load OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed.
    allow_credentials=True,
    allow_methods=["*"],  # Adjust this as needed.
    allow_headers=["*"],  # Adjust this as needed.
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Connect to MongoDB
db = get_database()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

@app.post("/upload-cv")
async def upload_cv(cv: UploadFile = File(...), job_field: str = Form(...)):
    try:
        # Read file content as binary
        cv_content = await cv.read()
        
        # Extract text from PDF
        pdf_text = ""
        with pdfplumber.open(io.BytesIO(cv_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text

        # Generate questions based on the CV text and job field
        questions = generate_questions(pdf_text, job_field)
        return {"questions": questions}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.post("/evaluate-answers")
async def evaluate_answers(answers: dict):
    score = evaluate_responses(answers)
    return JSONResponse(content={"score": score})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

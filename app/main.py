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
    try:
        score = evaluate_responses(answers)
        return JSONResponse(content={"score": score})
    except Exception as e:
        print(f"Error evaluating answers: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.post("/generate-coding-question")

async def generate_coding_question():
    try:
        # Generate the first coding question
        response1 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that generates coding questions for technical interviews."},
                {"role": "user", "content": "Generate a coding question for a technical interview."}
            ],
            max_tokens=100
        )
        coding_question_1 = response1.choices[0].message['content'].strip()

        # Generate the second coding question
        response2 = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that generates coding questions for technical interviews."},
                {"role": "user", "content": "Generate another coding question for a technical interview."}
            ],
            max_tokens=100
        )
        
        coding_question_2 = response2.choices[0].message['content'].strip()
        # Return both questions, the frontend can manage displaying one by one
        return {"questions": [coding_question_1, coding_question_2]}
    except Exception as e:
        print(f"Error generating coding questions: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")
@app.post("/evaluate-coding-solution")
async def evaluate_coding_solution(solution: str):
    try:
        # Create a prompt for evaluating the coding solution
        prompt = f"Evaluate the following coding solution. Provide a score from 1 to 10 based on correctness, efficiency, and clarity. Provide only the total score out of 10.\n\nSolution:\n{solution}\n\nScore:"

        # Call OpenAI API for evaluation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that evaluates coding solutions based on correctness, efficiency, and clarity. Provide only the total score out of 10 in your response."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        
        # Extract the total score from the response
        total_score = response.choices[0].message['content'].strip()
        
        return {"score": total_score}
    except Exception as e:
        print(f"Error evaluating coding solution: {e}")
        return {"score": "Error"}
@app.post("/speech-to-text")
async def speech_to_text(audio: UploadFile = File(...)):
    try:
        audio_content = await audio.read()

        # Use 'requests' to send a file-like object with 'name'
        import requests

        # Create a temporary file-like object with 'name' attribute
        class NamedBytesIO(io.BytesIO):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.name = kwargs.get('name', 'audio.wav')

        audio_file = NamedBytesIO(audio_content, name=audio.filename)

        response = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            format="wav"  # Ensure this matches the actual audio format
        )

        transcribed_text = response['text']
        return JSONResponse(content={"text": transcribed_text})

    except Exception as e:
        print(f"Error in speech-to-text conversion: {e}")
        return JSONResponse(content={"error": "An error occurred during speech-to-text conversion."}, status_code=500)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

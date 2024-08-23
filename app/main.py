from fastapi import FastAPI, File, UploadFile, Form, HTTPException
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
import requests

load_dotenv()

app = FastAPI()

# Load OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Add a global variable or a way to store the email address
email_address = None

@app.post("/upload-cv")
async def upload_cv(cv: UploadFile = File(...), job_field: str = Form(...)):
    global email_address
    try:
        cv_content = await cv.read()
        pdf_text = ""
        with pdfplumber.open(io.BytesIO(cv_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text

        # Extract email address from CV text (example extraction, adjust as needed)
        import re
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', pdf_text)
        email_address = email_match.group(0) if email_match else 'no-reply@example.com'

        questions = generate_questions(pdf_text, job_field)
        return {"questions": questions}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.post("/evaluate-answers")
async def evaluate_answers(answers: dict):
    try:
        score_response = evaluate_responses(answers)

        # Debugging output
        print("Received score response:", score_response)

        # Extract the numeric score from the response
        import re
        if isinstance(score_response, dict) and 'score' in score_response:
            # Use regex to extract the numeric score
            score_match = re.search(r'\d+', score_response['score'])
            score = int(score_match.group()) if score_match else None
        else:
            score = score_response
        # Ensure the score is a valid number
        if score is None or not isinstance(score, (int, float)):
            raise ValueError("Score is not a valid number.")
        
        # Send email if score is greater than 7
        if score > 7 and email_address != 'no-reply@example.com':
            subject = "Your Job Application Status"
            body = f"Congratulations! Your application score is {score}. You have been accepted."
            send_email(email_address, subject, body)

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

def send_email(to_address: str, subject: str, body: str):
    try:
        elastic_email_api_key = os.getenv('ELASTIC_EMAIL_API_KEY')
        response = requests.post(
            'https://api.elasticemail.com/v2/email/send',
            data={
                'apikey': elastic_email_api_key,
                'from': 'usmanmalik.dev@gmail.com',  # Replace with your Elastic Email sender address
                'to': to_address,
                'subject': subject,
                'text': body
            }
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.RequestException as e:
        print(f"Error sending email: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

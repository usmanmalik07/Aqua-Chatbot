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
import re
from mailjet_rest import Client
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
    global email_address, user_name
    try:
        cv_content = await cv.read()
        pdf_text = ""
        with pdfplumber.open(io.BytesIO(cv_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text

        # Use OpenAI to extract name and email address
        openai_prompt = f"""
        Extract the name and email address from the following CV text.
        Format your response as follows:
        - Name: [Full Name]
        - Email: [Email Address]

        The CV text is:
        {pdf_text}
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": openai_prompt}
            ],
            max_tokens=150,
            temperature=0
        )

        # Extract the result from the response
        extraction_result = response.choices[0].message['content'].strip()
        lines = extraction_result.split("\n")
        
        # Clean and format the extracted name and email
        def clean_text(text: str) -> str:
            return re.sub(r'[\s\-]+', ' ', text).strip()
        
        def clean_email(email: str) -> str:
            return re.sub(r'[^\w\.-@]', '', email).strip()

        if len(lines) >= 2:
            user_name = clean_text(lines[0].replace("Name: ", ""))
            email_address = clean_email(lines[1].replace("Email: ", ""))

        # Optional: Format the name for a more specific output
        formatted_name = f"{user_name}"
        
        questions = generate_questions(pdf_text, job_field)
        return {"questions": questions, "email_address": email_address, "user_name": formatted_name}
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.post("/evaluate-answers")
async def evaluate_answers(answers: dict):
    global email_address
    try:
        # Separate normal answers and coding answers
        normal_answers = {k: v for k, v in answers.items() if not k.startswith("coding_")}
        coding_answers = {k: v for k, v in answers.items() if k.startswith("coding_")}

        # Evaluate normal answers
        normal_scores = {}
        for question, answer in normal_answers.items():
            score = evaluate_responses({"question": question, "answer": answer})
            # Ensure the score is an integer
            normal_scores[question] = score["score"]

        # Evaluate coding answers
        coding_scores = {}
        for question, solution in coding_answers.items():
            response = await evaluate_coding_solution(solution)
            # Ensure the score is an integer
            coding_scores[question] = response["score"]

        # Calculate the total score
        total_score = sum(normal_scores.values()) + sum(coding_scores.values())
        total_score = total_score / (len(normal_answers) + len(coding_answers)) if (len(normal_answers) + len(coding_answers)) > 0 else 0

        # Send email regardless of the score
        if email_address and email_address != 'no-reply@example.com':
            subject = "Your Job Application Status"
            body = f"Your application has been evaluated. Your total score is {total_score}. Thank you for applying!"
            send_email(email_address, subject, body)

        return JSONResponse(content={"score": total_score})
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
        response = await openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that evaluates coding solutions based on correctness, efficiency, and clarity. Provide only the total score out of 10 in your response."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        
        # Extract the total score from the response
        total_score_str = response.choices[0].message['content'].strip()
        total_score = int(total_score_str) if total_score_str.isdigit() else 0
        
        return {"score": total_score}
    except Exception as e:
        print(f"Error evaluating coding solution: {e}")
        return {"score": 0}  # Return 0 in case of an error



def send_email(to_address: str, subject: str, body: str):
    try:
        mailjet_api_key = os.getenv('MAILJET_API_KEY')
        mailjet_secret_key = os.getenv('MAILJET_SECRET_KEY')

        if not mailjet_api_key or not mailjet_secret_key:
            raise ValueError("Mailjet API key or secret key not found in environment variables.")

        mailjet_client = Client(auth=(mailjet_api_key, mailjet_secret_key), version='v3.1')

        data = {
            'Messages': [
                {
                    'From': {
                        'Email': 'usmanmalikk2004@gmail.com',  # Replace with your Mailjet sender address
                        'Name': 'Your Name'
                    },
                    'To': [
                        {
                            'Email': to_address,
                            'Name': 'Recipient Name'
                        }
                    ],
                    'Subject': subject,
                    'TextPart': body
                }
            ]
        }

        result = mailjet_client.send.create(data=data)
        response_data = result.json()

        if result.status_code == 200:
            return {"status": "Email sent successfully."}
        else:
            # Log and raise an error with detailed response content
            error_message = response_data.get('ErrorMessage', 'Unknown error')
            print(f"Mailjet response: {response_data}")
            raise ValueError(f"Failed to send email: {error_message}")

    except requests.RequestException as e:
        print(f"RequestException: {e}")
        return {"error": str(e)}
    except ValueError as e:
        print(f"ValueError: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

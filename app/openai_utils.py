import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_questions(cv_text: str, job_field: str) -> list:
    try:
        # Generate questions using the new OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use "gpt-4" if you have access to it
            messages=[
                {"role": "system", "content": "You are an assistant that generates interview questions based on CV content."},
                {"role": "user", "content": f"Generate interview questions for a job in {job_field} based on the following CV text:\n{cv_text}"}
            ],
            max_tokens=150
        )
        questions = response.choices[0].message['content'].strip().split('\n')
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []
def evaluate_responses(responses: dict) -> dict:
    # Example implementation
    try:
        # Add your evaluation logic here
        scores = {key: len(value) for key, value in responses.items()}
        return scores
    except Exception as e:
        print(f"Error evaluating responses: {e}")
        return {}

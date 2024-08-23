import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_questions(cv_text: str, job_field: str) -> list:
    try:
        # Step 1: Check if the job field matches the CV text
        match_check_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that checks if a job field is relevant to the given CV text."},
                {"role": "user", "content": f"Does the job field '{job_field}' is relevant to the following CV text?\n{cv_text}"}
            ],
            max_tokens=50
        )
        match_result = match_check_response.choices[0].message['content'].strip().lower()
        
        # If the match result indicates no match, return an empty list or a message
        if "no" in match_result:
            return ["The job field does not match the CV text. No questions generated."]

        
        # Step 2: Generate questions based on the CV text and job field
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that generates interview questions based on CV content."},
                {"role": "user", "content": f"Generate interview questions for the job field '{job_field}' based on the following CV text:\n{cv_text}"}
            ],
            max_tokens=150
        )
        questions = response.choices[0].message['content'].strip().split('\n')
        return questions
    
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []
def evaluate_responses(responses: dict) -> dict:
    try:
        # Create a prompt for evaluating the answers
        prompt = "Evaluate the following answers to the interview questions. Provide a score from 1 to 10 based on completeness, relevance, and clarity. Provide a brief explanation for the score, but include only the total score out of 10 in the final response.\n\n"
        for question, answer in responses.items():
            prompt += f"Question: {question}\nAnswer: {answer}\n\n"
        
        # Add instructions for the evaluation
        prompt += "Please provide only the total score out of 10:\n"
        
        # Call OpenAI API for evaluation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use "gpt-4" if you have access to it
            messages=[
                {"role": "system", "content": "You are an assistant that evaluates answers to interview questions based on completeness, relevance, and clarity. Provide only the total score out of 10 in your response."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        
        # Extract the total score from the response
        total_score_str = response.choices[0].message['content'].strip()
        # Convert the score to an integer if possible, otherwise default to 0
        total_score = int(total_score_str) if total_score_str.isdigit() else 0
        
        return {"score": total_score}
    except Exception as e:
        print(f"Error evaluating responses: {e}")
        return {"score": 0}  # Return 0 in case of an error

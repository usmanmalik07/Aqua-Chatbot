from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import openai
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()
# Set your OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("templates/index.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

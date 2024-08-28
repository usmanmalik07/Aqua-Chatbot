# Aqua Jobs Filter Chatbot

<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua/blob/main/static/audio/logo1.png" height="40%" width="40%">
</div>

## Project Description

A job application chatbot where users can upload their CV and select their desired field. The model/app generates questions and problems based on the uploaded CV and the selected field. After answering all the questions, the model scores the user's interview and sends the results via email.

## Frontend Development

- HTML
- CSS
- JavaScript

## Backend Development

- Python

## APIs Used

- FastAPI
- OpenAI API
- MailJet API

## Tools and Technologies Used

- GitHub
- Google Colab
- Visual Studio Code
- Virtual Environment
- Command Line (CMD)

## Working

<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_2.png" height="100%" width="100%">
</div>
<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_1.png" height="100%" width="100%">
</div>
<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_3.png" height="100%" width="100%">
</div>
<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_4.png" height="100%" width="100%">
</div>
<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_5.png" height="100%" width="100%">
</div>
<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_6.png" height="100%" width="100%">
</div>
<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_7.png" height="100%" width="100%">
</div>
<div align="center">
  <img src="https://github.com/usmanmalik07/Aqua-Chatbot/blob/main/working/Screenshot_8.png" height="100%" width="100%">
</div>

## How to Clone and Run the Project

Follow these steps to clone the repository and run the Aqua Jobs Filter Chatbot project:

### 1. Install Git

Ensure that Git is installed on your system. If not, download and install it from [Git's official website](https://git-scm.com/downloads).

### 2. Clone the Repository

Open a terminal or command prompt, navigate to the directory where you want to clone the project, and run:

```bash
git clone https://github.com/usmanmalik07/Aqua-Chatbot.git
```

### 3. Navigate to the Project Directory
```bash
cd Aqua-Chatbot
```

### 4. Create a Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
```
Activate the Virtual Environment
On Windows
```bash
venv\Scripts\activate
```
On Linux
```bash
source venv/bin/activate
```
### 5. Install Dependencies

```bash
pip install -r requirements.txt
```
### 6. Run the Backend Server

```bash
uvicorn app.main:app --reload
```
This will start the server on http://127.0.0.1:8000.

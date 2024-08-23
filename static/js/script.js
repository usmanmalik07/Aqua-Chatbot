let currentQuestionIndex = 0;
let questions = [];
let codingQuestions = [];
let currentCodingQuestionIndex = 0;
let answers = {}; // To store answers for all questions

document.getElementById("submit-answers-button").style.display = "none";

// Function to show the spinner
function showSpinner() {
    document.getElementById("loading-spinner").style.display = "block";
}

// Function to hide the spinner
function hideSpinner() {
    document.getElementById("loading-spinner").style.display = "none";
}

async function uploadCv() {
    showSpinner();
    const formData = new FormData();
    formData.append("cv", document.getElementById("cv").files[0]);
    formData.append("job_field", document.getElementById("job_field").value);

    try {
        const response = await fetch("/upload-cv", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();

        console.log(result);

        if (result.questions && result.questions.length > 0 && result.questions[0] === "The job field does not match the CV text. No questions generated.") {
            displayTryAgainButton();
            const formElement = document.getElementById("cv-form");
            if (formElement) {
                formElement.style.display = "none";
            } else {
                console.error("Form element not found");
            }
        } else {
            // Hide the form container
            const formElement = document.getElementById("cv-form");
            if (formElement) {
                formElement.style.display = "none";
            } else {
                console.error("Form element not found");
            }

            // Display user info
            const userInfo = document.getElementById("user-info");
            if (userInfo) {
                userInfo.innerHTML = `
                    <p>Welcome, ${result.user_name}</p>
                    <p>Email: ${result.email_address}</p>
                `;
            } else {
                console.error("User info container not found");
            }

            questions = result.questions;
            displayNextQuestion();
        }
    } catch (error) {
        console.error("Error uploading CV:", error);
        alert("An error occurred while uploading the CV. Please try again.");
    } finally {
        hideSpinner(); // Hide spinner after the fetch completes
    }
}

function displayTryAgainButton() {
    const questionsContainer = document.getElementById("questions");
    questionsContainer.innerHTML = `
        <p>No questions generated as the job description doesn't match the CV text.</p>
        <button onclick="window.location.href='/'">Try Again</button>
    `;
}

function displayNextQuestion() {
    const questionsContainer = document.getElementById("questions");
    questionsContainer.innerHTML = `
        <p>${questions[currentQuestionIndex]}</p>
        <textarea id="answer"></textarea>
        <br>
        <button onclick="saveAnswer()">Next</button>
    `;
}

function saveAnswer() {
    const answer = document.getElementById("answer").value;
    answers[`question_${currentQuestionIndex + 1}`] = answer;
    currentQuestionIndex++;

    if (currentQuestionIndex < questions.length) {
        displayNextQuestion();
    } else {
        generateCodingQuestions();
    }
}

async function generateCodingQuestions() {
    showSpinner();
    try {
        const response = await fetch("/generate-coding-question", {
            method: "POST",
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();
        codingQuestions = result.questions;
        displayNextCodingQuestion();
    } catch (error) {
        console.error("Error generating coding questions:", error);
    } finally {
        hideSpinner(); // Hide spinner after the fetch completes
    }
}

function displayNextCodingQuestion() {
    const questionsContainer = document.getElementById("questions");
    questionsContainer.innerHTML = `
        <p>${codingQuestions[currentCodingQuestionIndex]}</p>
        <textarea id="coding_answer"></textarea>
        <br>
        <button onclick="saveCodingAnswer()">Next</button>
    `;
}

function saveCodingAnswer() {
    const answer = document.getElementById("coding_answer").value;
    answers[`coding_question_${currentCodingQuestionIndex + 1}`] = answer;
    currentCodingQuestionIndex++;

    if (currentCodingQuestionIndex < codingQuestions.length) {
        displayNextCodingQuestion();
    } else {
        document.getElementById("submit-answers-button").style.display = "block";
    }
}

async function submitAnswers() {
    showSpinner();
    try {
        const response = await fetch("/evaluate-answers", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(answers),
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();
        
        // Hide the questions box, answer fields, and buttons
        document.getElementById("questions").style.display = "none";
        document.getElementById("submit-answers-button").style.display = "none";

        // Display the score in the result-container
        const resultContainer = document.getElementById("result-container");
        resultContainer.innerHTML = `<h2>Your score: ${result.score}</h2>`;
        resultContainer.innerHTML = `<h2>Thankyou for applying. An email has been sent to you .</h2>`;
    } catch (error) {
        console.error("Error evaluating answers:", error);
        alert("An error occurred while evaluating the answers. Please try again.");
    } finally {
        hideSpinner(); // Hide spinner after the fetch completes
    }
}


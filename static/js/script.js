let currentQuestionIndex = 0;
let questions = [];
let codingQuestions = [];
let currentCodingQuestionIndex = 0;
let answers = {}; // To store answers for all questions

async function uploadCv() {
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
        questions = result.questions;
        displayNextQuestion();
    } catch (error) {
        console.error("Error uploading CV:", error);
        alert("An error occurred while uploading the CV. Please try again.");
    }
}

function displayNextQuestion() {
    const questionsContainer = document.getElementById("questions");
    questionsContainer.innerHTML = ""; // Clear previous question

    if (currentQuestionIndex < questions.length) {
        const questionElement = document.createElement("div");
        questionElement.innerHTML = `
            <label for="answer_${currentQuestionIndex}">${questions[currentQuestionIndex]}</label>
            <input type="text" id="answer_${currentQuestionIndex}" name="answers[${currentQuestionIndex}]" style="width: 100%; height: 100%">
            <div style="display: flex; justify-content: center; margin-top: 10px;">
                <button onclick="submitAnswer()" class="btn-submit">Done</button>
            </div>
        `;
        questionsContainer.appendChild(questionElement);
    } else {
        // All text-based questions answered, now generate coding questions
        getCodingQuestions();
    }
}

function submitAnswer() {
    const answerInput = document.querySelector(`#answer_${currentQuestionIndex}`);
    const answer = answerInput.value.trim();

    if (answer === "") {
        alert("Please provide an answer.");
        return;
    }

    // Store answer and move to the next question
    answers[`answer_${currentQuestionIndex}`] = answer;
    currentQuestionIndex++;
    displayNextQuestion();
}

async function getCodingQuestions() {
    try {
        const response = await fetch("/generate-coding-question", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();
        codingQuestions = result.questions;
        displayNextCodingQuestion();
    } catch (error) {
        console.error("Error fetching coding questions:", error);
        alert("An error occurred while fetching the coding questions. Please try again.");
    }
}

function displayNextCodingQuestion() {
    const codingQuestionContainer = document.getElementById("coding-question");
    codingQuestionContainer.innerHTML = ""; // Clear any previous coding question

    if (currentCodingQuestionIndex < codingQuestions.length) {
        codingQuestionContainer.innerHTML = `
            <h2>Coding Question ${currentCodingQuestionIndex + 1}</h2>
            <p>${codingQuestions[currentCodingQuestionIndex]}</p>
            <textarea id="coding-solution_${currentCodingQuestionIndex}" placeholder="Write your code here..." style="width: 100%; height: 100%;"></textarea>
            <div style="display: flex; justify-content: center; margin-top: 10px;">
                <button onclick="submitAnswer()" class="btn-submit">Done</button>
            </div>
        `;
    } else {
        evaluateAllAnswers();
    }
}

function submitCodingSolution() {
    const solution = document.getElementById(`coding-solution_${currentCodingQuestionIndex}`).value.trim();

    if (solution === "") {
        alert("Please provide a solution.");
        return;
    }

    // Store coding solution and move to the next coding question
    answers[`coding_solution_${currentCodingQuestionIndex}`] = solution;
    currentCodingQuestionIndex++;
    displayNextCodingQuestion();
}

async function evaluateAllAnswers() {
    try {
        const response = await fetch("/evaluate-all-answers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(answers),
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();
        alert(`Your total score is: ${result.score}`);
    } catch (error) {
        console.error("Error evaluating answers:", error);
        alert("An error occurred while evaluating your answers. Please try again.");
    }
}

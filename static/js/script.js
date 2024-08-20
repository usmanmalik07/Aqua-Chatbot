let currentQuestionIndex = 0;
let questions = [];
let codingQuestions = [];
let currentCodingQuestionIndex = 0;
let answers = {}; // To store answers for all questions
document.getElementById("submit-answers-button").disabled = true;

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

        // Debugging: Log result to see if data is coming correctly
        console.log(result);

        // Hide the form container
        const formElement = document.getElementById("cv-form");
        if (formElement) {
            formElement.style.display = "none";
        } else {
            console.error("Form element not found");
        }
        console.log(document.getElementById("cv-form"));

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
            <div style="display: flex; align-items: center;">
                <input type="text" id="answer_${currentQuestionIndex}" name="answers[${currentQuestionIndex}]" style="width: 100%; height: 100%">
                <button onclick="startSpeechRecognition(${currentQuestionIndex})" style="margin-left: 10px; background: none; border: none; cursor: pointer;">
                    <img src="/static/icons/microphone.png" alt="Speak" style="width: 24px; height: 24px;">
                </button>
            </div>
            <div style="display: flex; justify-content: center; margin-top: 10px;">
                <button onclick="submitAnswer()" class="btn-submit">Done</button>
            </div>
        `;
        questionsContainer.appendChild(questionElement);
    } else {
        getCodingQuestions();
    }
}

async function startSpeechRecognition(questionIndex) {
    try {
        const audioBlob = await recordAudio();
        const formData = new FormData();
        formData.append("audio", audioBlob, "audio.webm");

        const response = await fetch("/speech-to-text", {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to convert speech to text.");
        }

        const result = await response.json();
        document.getElementById(`answer_${questionIndex}`).value = result.text;
    } catch (error) {
        console.error("Error during speech recognition:", error);
        alert("An error occurred during speech recognition.");
    }
}
async function recordAudio() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    let audioChunks = [];

    return new Promise((resolve, reject) => {
        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
            resolve(audioBlob);
        };

        mediaRecorder.onerror = error => {
            reject(error);
        };

        mediaRecorder.start();

        // Stop recording after 5 seconds
        setTimeout(() => {
            mediaRecorder.stop();
        }, 5000); // Adjust the recording duration as needed
    });
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
                <button onclick="submitCodingSolution()" class="btn-submit" style="display: inline-block; padding: 12px 24px; margin: 10px 0; border: none; border-radius: 5px; background-color: #2a9d8f; color: #fff; font-size: 16px; cursor: pointer; transition: background-color 0.3s;">Done</button>
            </div>
        `;
    } else {
        // Once all coding questions are done, show the submit button
        codingQuestionContainer.innerHTML = `
            <button
                id="submit-answers-button"
                onclick="evaluateAllAnswers()"
                class="btn-submit"
            >
                Submit Answers
            </button>
        `;
        document.getElementById("submit-answers-button").disabled = false;
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
        const response = await fetch("/evaluate-answers", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(answers),
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();
        const score = parseFloat(result.score); // Ensure score is treated as a number

        // Display the score and application status
        const resultContainer = document.getElementById("result-container");
        if (!resultContainer) {
            // Create a container if it doesn't exist
            const newResultContainer = document.createElement("div");
            newResultContainer.id = "result-container";
            document.body.appendChild(newResultContainer);
        }

        const message = score >= 7
            ? "Your application has been accepted!"
            : "Your application has been rejected.";

        document.getElementById("result-container").innerHTML = `
            <p>Your total score is: ${score}</p>
            <p style="font-weight: bold; color: ${score >= 7 ? 'green' : 'red'};">${message}</p>
        `;
    } catch (error) {
        console.error("Error evaluating answers:", error);
        alert("An error occurred while evaluating your answers. Please try again.");
    }
}

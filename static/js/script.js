// scripts.js
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
        displayQuestions(result.questions);
    } catch (error) {
        console.error("Error uploading CV:", error);
        alert("An error occurred while uploading the CV. Please try again.");
    }
}

function displayQuestions(questions) {
    const questionsContainer = document.getElementById("questions");
    questionsContainer.innerHTML = ""; // Clear previous questions

    questions.forEach((question, index) => {
        const questionElement = document.createElement("div");
        questionElement.innerHTML = `
            <label for="answer_${index}">${question}</label>
            <input type="text" id="answer_${index}" name="answers[${index}]">
        `;
        questionsContainer.appendChild(questionElement);
    });
}

async function evaluateAnswers() {
    const answers = Array.from(
        document.querySelectorAll("#questions input")
    ).reduce((acc, input) => {
        acc[input.name] = input.value;
        return acc;
    }, {});

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
        alert(`Your total score is: ${result.score}`);
    } catch (error) {
        console.error("Error evaluating answers:", error);
        alert("An error occurred while evaluating your answers. Please try again.");
    }
}
async function getCodingQuestion() {
    try {
        const response = await fetch("/generate-coding-question", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();
        displayCodingQuestion(result.question);
    } catch (error) {
        console.error("Error fetching coding question:", error);
        alert("An error occurred while fetching the coding question. Please try again.");
    }
}
function displayCodingQuestion(question) {
    const codingQuestionContainer = document.getElementById("coding-question");
    codingQuestionContainer.innerHTML = `
        <h2>Coding Question</h2>
        <p>${question}</p>
        <textarea id="coding-solution" placeholder="Write your code here..."></textarea>
        <button onclick="submitCodingSolution()" class="btn-submit">Submit Solution</button>
    `;
}
async function submitCodingSolution() {
    const solution = document.getElementById("coding-solution").value;

    try {
        const response = await fetch("/evaluate-coding-solution", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ solution })
        });

        if (!response.ok) {
            throw new Error("Network response was not ok.");
        }

        const result = await response.json();
        alert(`Your coding solution score is: ${result.score}`);
    } catch (error) {
        console.error("Error evaluating coding solution:", error);
        alert("An error occurred while evaluating your coding solution. Please try again.");
    }
}


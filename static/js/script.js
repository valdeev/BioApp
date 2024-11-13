let preguntas = [];
let currentQuestionIndex = 0;
let userResponses = [];


let questionElement, answerButtonsElement, nextButton;


document.addEventListener("DOMContentLoaded", () => {
    questionElement = document.getElementById("question");
    answerButtonsElement = document.getElementById("answer-buttons");
    nextButton = document.getElementById("next-btn");
    finaltest = document.getElementById("finaltest")
    quiz = document.getElementById("quiz")

    if (!questionElement || !answerButtonsElement || !nextButton) {
        console.error("Error al seleccionar elementos del DOM");
        return;
    }


    nextButton.style.display = "none";
    finaltest.style.display = "none"


    loadQuestions();


    nextButton.addEventListener("click", () => {
        currentQuestionIndex++;
        if (currentQuestionIndex < preguntas.questions.length) {
            showQuestion();
        } else {
            quiz.style.display = "none"
            finaltest.style.display = "block"
            submitAnswers();
        }
    });
});


async function loadQuestions() {
    try {
        const response = await fetch('/questions');
        preguntas = await response.json();
        showQuestion();
    } catch (error) {
        console.error("Error al cargar el archivo JSON:", error);
    }
}


function showQuestion() {
    answerButtonsElement.innerHTML = "";

    const currentQuestion = preguntas.questions[currentQuestionIndex];


    if (!currentQuestion) {
        console.error(`No se encontró la pregunta en el índice ${currentQuestionIndex}`);
        return;
    }
    questionNro = currentQuestionIndex + 1;
    questionElement.innerText = questionNro + ". " + currentQuestion.text;


    currentQuestion.answers.forEach(answer => {
        const button = document.createElement("button");
        button.classList.add("btn");
        button.innerText = answer.text;
        button.dataset.biotype = answer.biotype;
        button.dataset.points = answer.points;
        button.addEventListener("click", selectAnswer);
        answerButtonsElement.appendChild(button);
    });

    nextButton.style.display = "none";
}



function selectAnswer(event) {
    const selectedButton = event.target;
    const biotype = selectedButton.dataset.biotype;
    const points = parseInt(selectedButton.dataset.points);

    const allButtons = answerButtonsElement.querySelectorAll(".btn");
    allButtons.forEach(button => {
        button.classList.remove("selected");
    });
    selectedButton.classList.add("selected");

    userResponses.push({ biotype, points });
    nextButton.style.display = "block";
}


function submitAnswers() {
    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responses: userResponses })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            // nada
        }
    })
    .catch(error => console.error('Error al enviar respuestas:', error));
}
let phrases = [];
let currentQuestionIndex = 0;
let userResponses = { left: 0, right: 0 };
let questionElement, answerButtonsElement, nextButton, startTestButton, allButtons, quiz, finaltest;

document.addEventListener("DOMContentLoaded", () => {
    questionElement = document.getElementById("question");
    answerButtonsElement = document.getElementById("answer-buttons");
    nextButton = document.getElementById("next-btn");
    startTestButton = document.getElementById("start-test");
    quiz = document.getElementById("quiz");
    finaltest = document.getElementById("finaltest");

    finaltest.style.display = "none";
    nextButton.style.display = "none";
    answerButtonsElement.style.display = "none";
    startTestButton.addEventListener("click", startTest);
    nextButton.addEventListener("click", showNextQuestion);
    loadPhrases();
});


async function loadPhrases() {
    try {
        const response = await fetch('/phrases');
        phrases = await response.json();
    } catch (error) {
        console.error("Error al cargar las frases:", error);
    }
}


function startTest() {
    startTestButton.style.display = "none";
    answerButtonsElement.style.display = "block";
    showQuestion();
}


function showQuestion() {
    nextButton.style.display = "none";
    allButtons = document.querySelectorAll(".range-button");

    const currentQuestion = phrases.frases[currentQuestionIndex];
    if (!currentQuestion) {
        console.error(`No se encontró la pregunta en el índice ${currentQuestionIndex}`);
        return;
    }

    questionElement.innerText = currentQuestion;
    resetButtonStyles();


    allButtons.forEach(button => {
        button.addEventListener("click", selectAnswer);
    });
}


function resetButtonStyles() {
    allButtons.forEach(button => {
        button.classList.remove("selected");
    });
}


function selectAnswer(event) {
    const selectedButton = event.target;
    resetButtonStyles();
    selectedButton.classList.add("selected");
    nextButton.style.display = "block";
}


function showNextQuestion() {
    saveResponse(); 
    currentQuestionIndex++;

    if (currentQuestionIndex < phrases.frases.length) {
        showQuestion(); 
    } else {
        endQuiz();
    }
}


function saveResponse() {
    const selectedButton = document.querySelector(".range-button.selected");
    if (selectedButton) {
        const selectedValue = parseInt(selectedButton.innerText);


        if (currentQuestionIndex % 2 === 0) {
            userResponses.left += selectedValue;
        } else {
            userResponses.right += selectedValue;
        }
    } else {
        console.error("No se seleccionó ninguna respuesta.");
    }
}


function endQuiz() {
    quiz.style.display = "none";
    finaltest.style.display = "block";

    fetch('/save_results', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            left: userResponses.left,
            right: userResponses.right
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error en la respuesta del servidor: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        //
    })
    .catch(error => console.error("Error al enviar los resultados:", error));
}

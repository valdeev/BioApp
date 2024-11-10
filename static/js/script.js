function submitAnswers() {
    const form = document.getElementById('questionnaire');
    const responses = [];
    const inputs = form.querySelectorAll('input[type="radio"]:checked');

    inputs.forEach(input => {
        responses.push({
            biotype: input.value,
            points: parseInt(input.getAttribute('data-points'))
        });
    });

    fetch('/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ responses: responses })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            alert(`Tu biotipo predominante es: ${data.biotype}`);
            console.log("Desglose de puntuación:", data.scores);
        }
    })
    .catch(error => console.error('Error:', error));
}

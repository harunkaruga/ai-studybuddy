const notesEl = document.getElementById('notes');
const generateBtn = document.getElementById('generate');
const cardsEl = document.getElementById('cards');
const statusEl = document.getElementById('status');

generateBtn.addEventListener('click', async () => {
    const notes = notesEl.value.trim();
    if (!notes) {
        statusEl.textContent = "Please paste some notes first.";
        return;
    }

    statusEl.textContent = "Generating flashcards... (this may take a few seconds)";
    cardsEl.innerHTML = "";

    try {
        const res = await fetch("/generate", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({notes})
        });
        const data = await res.json();
        if (data.cards && data.cards.length > 0) {
            data.cards.forEach(card => {
                const div = document.createElement("div");
                div.className = "card";
                div.innerText = `Q: ${card.question}\n\nA: ${card.answer}`;
                cardsEl.appendChild(div);
            });
            statusEl.textContent = "Flashcards generated!";
        } else {
            statusEl.textContent = "No flashcards generated.";
        }
    } catch (err) {
        statusEl.textContent = "Error: " + err.message;
    }
});

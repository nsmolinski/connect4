document.getElementById('new-game').addEventListener('click', () => {
    fetch('http://127.0.0.1:5000/api/game', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            // Przejście do strony gry
            window.location.href = `templates/game.html?game_id=${data.game_id}`;
        });
});

document.getElementById('join-game').addEventListener('click', () => {
    const roomCode = document.getElementById('room-code').value.trim();
    fetch(`http://127.0.0.1:5000/api/join/${roomCode}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'joined') {
                // Przejście do strony gry
                window.location.href = `templates/game.html?game_id=${data.game_id}`;
            } else {
                alert(data.error);
            }
        });
});
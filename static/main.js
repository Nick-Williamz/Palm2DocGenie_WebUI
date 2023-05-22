var topicForm = document.getElementById('topic-form');
if (topicForm) {
    topicForm.addEventListener('submit', function(event) {
        event.preventDefault();

        var topic = document.getElementById('topic').value;
        
        fetch('/generate-section', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'topic=' + encodeURIComponent(topic)
        })
        .then(response => response.json())
        .then(data => {
            var output = document.getElementById('output');
            if (data.error) {
                output.textContent = data.error;
            } else {
                output.innerHTML = '<span style="color: #27c93f; font-weight: bold;">Your Question:</span><br>' 
                + topic + 
                '<br><br><span style="color: #FBBD00; font-weight: bold;">Genie Says:</span><br>'
                + data.section +
                '<br><span style="color: red; font-weight: bold;">Cosine Similarity:</span><br>'
                + data.cosine_similarity.toFixed(2)
            }
            // Show the output div after getting the response
            output.style.display = 'block';
        });
    });
}
function submitChatForm(event) {
    event.preventDefault();
    var message = document.getElementById('message').value;

    console.log('Submitting message:', message); // Add this line for debugging

    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'message=' + encodeURIComponent(message)
    })
        .then(response => {
            console.log('Response received:', response); // Add this line for debugging
            return response.json();
        })
        .then(data => {
            console.log('Data received:', data); // Add this line for debugging

            var chatContainer = document.getElementById('chat-output');
            if (data.error) {
                chatContainer.innerHTML += '<p class="error">' + data.error + '</p>';
            } else {
                chatContainer.innerHTML += '<p style="font-weight:bold">Your Query: </p>' + message + '\n'; // Add newline character here
                chatContainer.innerHTML += '<p style="font-weight:bold">Genie Says: </p>' + data.model_response + '\n'; // Add newline character here
            }
            chatContainer.scrollTop = chatContainer.scrollHeight;
        });
}
function saveChat() {
    const chatContent = document.getElementById('chat-output').textContent;
    const blob = new Blob([chatContent], { type: "text/plain;charset=utf-8" });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'chat-session.txt';
    link.click();
}
document.getElementById('save-button').addEventListener('click', saveChat);

var clearDocument = document.getElementById('clear-document-btn');
if (clearDocument) {
    clearDocument.addEventListener('click', function(event) {
        event.preventDefault();

        fetch('/clear-document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: 'clear_output=true'
        })
        .then(response => response.text())
        .then(data => {
            var output = document.getElementById('output');
            output.textContent = ''; // Clear the output section
            // Hide the output div after clearing the output
            output.style.display = 'none';
        });
    });
}


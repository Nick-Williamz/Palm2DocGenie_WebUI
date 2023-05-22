document.getElementById('topic-form').addEventListener('submit', function(event) {
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
            output.innerHTML = '<span style="color: #27c93f; font-weight: bold;">Your Question:</span><br>' + topic + '<br><span style="color: #FBBD00; font-weight: bold;">Genie Says:</span><br>' + data.section + '<br><span style="color: red; font-weight: bold;">Cosine Similarity:</span><br>' + data.cosine_similarity.toFixed(2);
        }
        // Show the output div after getting the response
        output.style.display = 'block';
    });
});
document.getElementById('clear-document-btn').addEventListener('click', function(event) {
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
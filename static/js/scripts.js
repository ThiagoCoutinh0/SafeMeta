document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    
    var fileInput = document.getElementById('file-input');
    var file = fileInput.files[0];
    var formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        var display = document.getElementById('metadata-display');
        display.textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error:', error));
});

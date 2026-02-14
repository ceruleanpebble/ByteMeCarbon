const dropZone = document.getElementById('drop-zone');
const results = document.getElementById('results');

// Handle Drop Events
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(evt => {
    dropZone.addEventListener(evt, e => e.preventDefault());
});

dropZone.addEventListener('drop', e => {
    const file = e.dataTransfer.files[0];
    if (file?.name.endsWith('.py')) handleFile(file);
});

document.getElementById('file-input').addEventListener('change', e => {
    handleFile(e.target.files[0]);
});

function handleFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const content = e.target.result;
        // Switch views with a smooth fade
        dropZone.style.opacity = '0';
        setTimeout(() => {
            dropZone.classList.add('hidden');
            results.classList.remove('hidden');
            document.getElementById('original-display').textContent = content;
            simulateOptimization(content);
        }, 400);
    };
    reader.readAsText(file);
}

function handleFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        dropZone.style.opacity = '0';
        setTimeout(() => {
            dropZone.classList.add('hidden');
            results.classList.remove('hidden');

            document.getElementById('original-display').textContent = data.original;
            document.getElementById('optimized-display').textContent = data.optimized;
            document.getElementById('energy-stat').textContent = data.energy_saved;
        }, 400);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Backend connection failed.");
    });
}
function resetUI() {
    location.reload(); // Simple way to reset the parallax state
}
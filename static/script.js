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
    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        // Display code
        document.getElementById('original-display').textContent = data.original;
        document.getElementById('optimized-display').textContent = data.optimized;

        // Extract and display report data
        const report = data.report;
        displayReport(report);

        // Show results
        dropZone.style.opacity = '0';
        setTimeout(() => {
            dropZone.classList.add('hidden');
            results.classList.remove('hidden');
        }, 400);
    })
    .catch(error => {
        console.error("Error:", error);
        alert("Backend connection failed.");
    });
}

function displayReport(report) {
    // Complexity
    document.getElementById('complexity-before').textContent = report.complexity.before;
    document.getElementById('complexity-after').textContent = report.complexity.after;

    // Performance
    document.getElementById('performance-status').textContent = report.performance.status;
    document.getElementById('performance-detail').textContent = 
        `${report.performance.baseline_time} → ${report.performance.optimized_time}`;

    // Energy
    document.getElementById('energy-status').textContent = report.energy.status;
    document.getElementById('energy-detail').textContent = 
        `${report.energy.baseline_co2} → ${report.energy.optimized_co2}`;

    // Real-world impact
    const impact = report.real_world_impact;
    if (impact.message) {
        // No measurable change
        document.getElementById('impact-section').style.display = 'none';
    } else if (impact.per_run) {
        document.getElementById('impact-section').style.display = 'block';
        
        const perRunText = `${impact.per_run.co2_saved} | ${impact.per_run.energy_saved}`;
        document.getElementById('impact-per-run').textContent = perRunText;

        if (impact.projected_yearly) {
            const yearly = impact.projected_yearly;
            const yearlyText = `${yearly.co2_saved} | ${yearly.energy_saved}<br>` +
                `🚗 ${yearly.equivalents.electric_car_distance}<br>` +
                `💻 ${yearly.equivalents.laptop_full_charges}`;
            document.getElementById('impact-yearly').innerHTML = yearlyText;
        }
    }
}

function resetUI() {
    location.reload();
}
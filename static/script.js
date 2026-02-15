// DOM Elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const optimizeBtn = document.getElementById('optimize-btn');
const placeholder = document.getElementById('placeholder');
const resultsContent = document.getElementById('results-content');

let uploadedFile = null;

// File Upload Handling
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('dragover');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('dragover');
    }, false);
});

dropZone.addEventListener('drop', handleDrop, false);
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
}

function handleFileSelect(file) {
    if (!file.name.endsWith('.py')) {
        alert('Please upload a Python (.py) file');
        return;
    }
    
    uploadedFile = file;
    dropZone.innerHTML = `
        <div class="upload-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
        </div>
        <p class="drop-text">File selected: <span class="highlight-text">${file.name}</span></p>
    `;
    optimizeBtn.disabled = false;
}

// Optimize Button Click Handler
optimizeBtn.addEventListener('click', () => {
    if (!uploadedFile) {
        alert('Please upload a file first');
        return;
    }
    
    optimizeBtn.disabled = true;
    optimizeBtn.innerHTML = '<span class="btn-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 2v20M2 12h20"></path><animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/></svg></span> Processing...';
    
    const formData = new FormData();
    formData.append('file', uploadedFile);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
            resetOptimizeButton();
            return;
        }
        
        displayResults(data);
        optimizeBtn.innerHTML = '<span class="btn-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg></span> Optimization Complete';
        
        // Reload user stats after successful optimization
        loadUserStats();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Failed to connect to server');
        resetOptimizeButton();
    });
});

function resetOptimizeButton() {
    optimizeBtn.disabled = false;
    optimizeBtn.innerHTML = '<span class="btn-icon"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg></span> Optimize Code';
}

function displayResults(data) {
    console.log('Displaying results:', data);
    
    // Display code
    document.getElementById('original-display').textContent = data.original;
    document.getElementById('optimized-display').textContent = data.optimized;
    
    // Show results panel
    placeholder.classList.add('hidden');
    resultsContent.classList.remove('hidden');
    
    // Display metrics from report
    const report = data.report;
    console.log('Report data:', report);
    
    // Complexity
    const complexityText = `${report.complexity.before} → ${report.complexity.after}`;
    document.getElementById('complexity-value').textContent = complexityText;
    
    // Time - use numeric values from report
    const baselineTime = report.performance.baseline_time;
    const optimizedTime = report.performance.optimized_time;
    const timeText = `${(baselineTime * 1000).toFixed(2)}ms → ${(optimizedTime * 1000).toFixed(2)}ms`;
    document.getElementById('time-value').textContent = timeText;
    
    // Energy Saved - use numeric values (already in grams)
    const baselineCO2 = report.energy.baseline_co2;
    const optimizedCO2 = report.energy.optimized_co2;
    const energySaved = baselineCO2 - optimizedCO2;
    document.getElementById('energy-value').textContent = energySaved.toFixed(6) + 'g CO₂';
    
    // CO2 Impact
    document.getElementById('co2-value').textContent = optimizedCO2.toFixed(6) + 'g';
    
    // Efficiency Score (calculated based on improvements)
    const efficiency = calculateEfficiencyScore(report);
    document.getElementById('efficiency-value').textContent = efficiency;
    
    // Real-world impact projections
    if (report.real_world_impact && !report.real_world_impact.message) {
        const impact = report.real_world_impact;
        console.log('Impact data:', impact);
        
        // Parse yearly values
        if (impact.projected_yearly) {
            const yearly = impact.projected_yearly;
            
            // Extract numeric values from strings
            const kwhMatch = yearly.energy_saved.match(/[\d.]+/);
            const kwhValue = kwhMatch ? parseFloat(kwhMatch[0]).toFixed(4) : '0';
            document.getElementById('yearly-kwh').textContent = kwhValue;
            
            // LED usage hours (10W LED)
            if (yearly.equivalents && yearly.equivalents.led_10w_usage) {
                const ledMatch = yearly.equivalents.led_10w_usage.match(/[\d.]+/);
                const ledValue = ledMatch ? parseFloat(ledMatch[0]).toFixed(2) : '0';
                document.getElementById('led-usage').textContent = ledValue;
            } else {
                document.getElementById('led-usage').textContent = '0';
            }
            
            // Electric car distance
            if (yearly.equivalents && yearly.equivalents.electric_car_distance) {
                const carMatch = yearly.equivalents.electric_car_distance.match(/[\d.]+/);
                const carValue = carMatch ? parseFloat(carMatch[0]).toFixed(2) : '0';
                document.getElementById('car-distance').textContent = carValue;
            } else {
                document.getElementById('car-distance').textContent = '0';
            }
            
            // Laptop charges
            if (yearly.equivalents && yearly.equivalents.laptop_full_charges) {
                const laptopMatch = yearly.equivalents.laptop_full_charges.match(/[\d.]+/);
                const laptopValue = laptopMatch ? parseFloat(laptopMatch[0]).toFixed(2) : '0';
                document.getElementById('laptop-charges').textContent = laptopValue;
            } else {
                document.getElementById('laptop-charges').textContent = '0';
            }
        }
    } else {
        // Set zeros if no significant impact
        document.getElementById('yearly-kwh').textContent = '0';
        document.getElementById('led-usage').textContent = '0';
        document.getElementById('car-distance').textContent = '0';
        document.getElementById('laptop-charges').textContent = '0';
    }
}

function calculateEfficiencyScore(report) {
    
    let score = 0;
    
    try {
        
        const beforeComp = report.complexity.before;
        const afterComp = report.complexity.after;
        if (beforeComp !== afterComp) {
            score += 40;
        }
        
        const beforeTime = report.performance.baseline_time;
        const afterTime = report.performance.optimized_time;
        
        if (afterTime < beforeTime) {
            const improvement = ((beforeTime - afterTime) / beforeTime) * 100;
            score += Math.min(30, improvement * 3);
        }
        
        const beforeEnergy = report.energy.baseline_co2;
        const afterEnergy = report.energy.optimized_co2;
        
        if (afterEnergy < beforeEnergy) {
            const improvement = ((beforeEnergy - afterEnergy) / beforeEnergy) * 100;
            score += Math.min(30, improvement * 3);
        }
    } catch (e) {
        console.error('Error calculating efficiency score:', e);
    }
    
    return Math.round(score);
}

function resetUI() {
    location.reload();
}

// User Stats and History
document.addEventListener('DOMContentLoaded', () => {
    loadUserStats();
    setupHistoryModal();
});

async function loadUserStats() {
    try {
        const response = await fetch('/api/user/stats');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('total-energy').textContent = `${data.total_energy_saved.toFixed(6)} kWh`;
            document.getElementById('total-optimizations').textContent = data.total_optimizations;
        }
    } catch (error) {
        console.error('Error loading user stats:', error);
    }
}

function setupHistoryModal() {
    const viewHistoryBtn = document.getElementById('view-history-btn');
    const historyModal = document.getElementById('history-modal');
    const closeHistoryModal = document.getElementById('close-history-modal');
    const detailModal = document.getElementById('detail-modal');
    const closeDetailModal = document.getElementById('close-detail-modal');
    
    viewHistoryBtn.addEventListener('click', async () => {
        historyModal.style.display = 'flex';
        await loadHistory();
    });
    
    closeHistoryModal.addEventListener('click', () => {
        historyModal.style.display = 'none';
    });
    
    closeDetailModal.addEventListener('click', () => {
        detailModal.style.display = 'none';
    });
    
    // Close on outside click
    historyModal.addEventListener('click', (e) => {
        if (e.target === historyModal) {
            historyModal.style.display = 'none';
        }
    });
    
    detailModal.addEventListener('click', (e) => {
        if (e.target === detailModal) {
            detailModal.style.display = 'none';
        }
    });
    
    // Setup detail tabs
    const detailTabs = document.querySelectorAll('.detail-tab');
    detailTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabName = tab.dataset.tab;
            detailTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            document.querySelectorAll('.detail-tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(`detail-${tabName}`).classList.add('active');
        });
    });
}

async function loadHistory() {
    const historyList = document.getElementById('history-list');
    historyList.innerHTML = '<div class="loading">Loading history...</div>';
    
    try {
        const response = await fetch('/api/history');
        if (response.ok) {
            const data = await response.json();
            
            if (data.history.length === 0) {
                historyList.innerHTML = '<div class="empty-state">No optimization history yet. Upload a file to get started!</div>';
                return;
            }
            
            historyList.innerHTML = '';
            data.history.forEach(item => {
                const historyItem = createHistoryItem(item);
                historyList.appendChild(historyItem);
            });
        } else {
            historyList.innerHTML = '<div class="empty-state">Failed to load history</div>';
        }
    } catch (error) {
        console.error('Error loading history:', error);
        historyList.innerHTML = '<div class="empty-state">Error loading history</div>';
    }
}

function createHistoryItem(item) {
    const div = document.createElement('div');
    div.className = 'history-item';
    
    const date = new Date(item.created_at).toLocaleString();
    
    div.innerHTML = `
        <div class="history-item-info">
            <div class="history-item-filename">${item.filename}</div>
            <div class="history-item-meta">
                <span>📅 ${date}</span>
                <span>⚡ ${item.before_complexity} → ${item.after_complexity}</span>
                <span>💚 ${item.energy_saved.toFixed(6)} kWh saved</span>
            </div>
        </div>
        <div class="history-item-actions">
            <button class="history-item-btn view-btn" onclick="viewHistoryDetail(${item.id})">View</button>
            <button class="history-item-btn delete-btn" onclick="deleteHistoryItem(${item.id})">Delete</button>
        </div>
    `;
    
    return div;
}

async function viewHistoryDetail(id) {
    try {
        const response = await fetch(`/api/history/${id}`);
        if (response.ok) {
            const item = await response.json();
            
            // Set filename
            document.getElementById('detail-filename').textContent = item.filename;
            
            // Set code
            document.getElementById('original-code-detail').textContent = item.original_code;
            document.getElementById('optimized-code-detail').textContent = item.optimized_code;
            
            // Set metrics
            const metricsContent = document.getElementById('metrics-content');
            metricsContent.innerHTML = `
                <div class="metric-detail">
                    <div class="metric-detail-label">Complexity Before</div>
                    <div class="metric-detail-value">${item.before_complexity}</div>
                </div>
                <div class="metric-detail">
                    <div class="metric-detail-label">Complexity After</div>
                    <div class="metric-detail-value">${item.after_complexity}</div>
                </div>
                <div class="metric-detail">
                    <div class="metric-detail-label">Energy Saved</div>
                    <div class="metric-detail-value">${item.energy_saved.toFixed(6)} kWh</div>
                </div>
                <div class="metric-detail">
                    <div class="metric-detail-label">CO₂ Reduced</div>
                    <div class="metric-detail-value">${item.co2_reduced.toFixed(6)} kg</div>
                </div>
                <div class="metric-detail">
                    <div class="metric-detail-label">Time Saved</div>
                    <div class="metric-detail-value">${item.time_saved.toFixed(4)}s/year</div>
                </div>
                <div class="metric-detail">
                    <div class="metric-detail-label">Date</div>
                    <div class="metric-detail-value" style="font-size: 0.9rem;">${new Date(item.created_at).toLocaleDateString()}</div>
                </div>
            `;
            
            // Show detail modal
            document.getElementById('detail-modal').style.display = 'flex';
            
            // Reset to first tab
            document.querySelectorAll('.detail-tab').forEach(t => t.classList.remove('active'));
            document.querySelector('.detail-tab[data-tab="original"]').classList.add('active');
            document.querySelectorAll('.detail-tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById('detail-original').classList.add('active');
        }
    } catch (error) {
        console.error('Error loading history detail:', error);
        alert('Failed to load history details');
    }
}

async function deleteHistoryItem(id) {
    if (!confirm('Are you sure you want to delete this item from your history?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/history/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            await loadHistory();
            await loadUserStats(); // Refresh stats after deletion
        } else {
            alert('Failed to delete history item');
        }
    } catch (error) {
        console.error('Error deleting history item:', error);
        alert('Failed to delete history item');
    }
}
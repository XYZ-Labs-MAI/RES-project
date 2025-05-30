const uploadForm = document.getElementById('uploadForm');
const imageUpload = document.getElementById('imageUpload');
const statusDiv = document.getElementById('status');
const resultsSection = document.getElementById('resultsSection');
const canvas = document.getElementById('detectionCanvas');
const container = document.getElementById('canvasContainer');
const overlay = document.getElementById('canvasOverlay');
const filterControls = document.getElementById('filterControls');
const listUl = document.getElementById('detectionList');
const errorDiv = document.getElementById('errorDisplay');
const confSlider = document.getElementById('confSlider');
const confValue = document.getElementById('confValue');
const zoomInBtn = document.getElementById('zoomIn');
const zoomOutBtn = document.getElementById('zoomOut');
const resetViewBtn = document.getElementById('resetView');
const objectsCount = document.getElementById('objectsCount');
const ctx = canvas.getContext('2d');

let loadedImage = null;
let allObjects = [];
let filters = {};
let minConfidence = 0;
let scale = 1, translateX = 0, translateY = 0;
let isDragging = false, dragStartX = 0, dragStartY = 0, startX = 0, startY = 0;

// Initialize confidence slider
confValue.textContent = '0%';
confSlider.value = '0';

// File input change handler
imageUpload.addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : 'No file selected';
    document.getElementById('fileName').textContent = fileName;
});

// Form submission handler
uploadForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const file = imageUpload.files[0];
    if (!file) {
        showError('Please select an image file first');
        return;
    }
    
    setStatus('Uploading image and processing...');
    hideError();
    resetView();
    
    // Show loading state
    overlay.style.display = 'flex';
    overlay.querySelector('.overlay-content i').className = 'fas fa-spinner fa-spin';
    overlay.querySelector('.overlay-content p').textContent = 'Processing image...';
    
    const url = URL.createObjectURL(file);
    loadedImage = new Image();
    loadedImage.src = url;
    
    loadedImage.onload = function() {
        canvas.width = loadedImage.naturalWidth;
        canvas.height = loadedImage.naturalHeight;
        
        const formData = new FormData(uploadForm);
        
        // Original detection logic
        fetch('/detection/upload/', { 
            method: 'POST',
            body: formData 
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.task_id) {
                poll(data.task_id);
            } else {
                throw new Error(data.error || 'Unknown error occurred');
            }
        })
        .catch(error => {
            showError('Error: ' + error.message);
            setStatus('Ready for new upload');
            overlay.style.display = 'flex';
            overlay.querySelector('.overlay-content i').className = 'fas fa-image';
            overlay.querySelector('.overlay-content p').textContent = 'Upload an image to begin detection';
        });
    };
});

// Confidence slider handler
confSlider.addEventListener('input', function() {
    minConfidence = this.value / 100;
    confValue.textContent = this.value + '%';
    if (allObjects.length) {
        drawBoxes(allObjects);
        updateObjectsCount();
    }
});

// Zoom controls
zoomInBtn.addEventListener('click', function() {
    scale *= 1.2;
    drawBoxes(allObjects);
});

zoomOutBtn.addEventListener('click', function() {
    scale /= 1.2;
    drawBoxes(allObjects);
});

resetViewBtn.addEventListener('click', resetView);

// Canvas interaction handlers
canvas.addEventListener('wheel', function(e) {
    e.preventDefault();
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const factor = e.deltaY < 0 ? 1.1 : 0.9;
    const x = (mx - translateX) / scale;
    const y = (my - translateY) / scale;
    scale *= factor;
    translateX = mx - x * scale;
    translateY = my - y * scale;
    drawBoxes(allObjects);
});

canvas.addEventListener('mousedown', function(e) {
    isDragging = true;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    startX = translateX;
    startY = translateY;
    container.style.cursor = 'grabbing';
});

window.addEventListener('mousemove', function(e) {
    if (!isDragging) return;
    translateX = startX + (e.clientX - dragStartX);
    translateY = startY + (e.clientY - dragStartY);
    drawBoxes(allObjects);
});

window.addEventListener('mouseup', function() {
    isDragging = false;
    container.style.cursor = 'grab';
});

// Original poll function
function poll(taskId) {
    statusDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing image...';
    
    const interval = setInterval(function() {
        fetch(`/detection/result/${taskId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.task_status === 'SUCCESS') {
                clearInterval(interval);
                handleDetectionSuccess(data);
            } else if (data.task_status === 'FAILURE') {
                clearInterval(interval);
                showError('Detection failed');
                setStatus('Ready for new upload');
            }
        })
        .catch(error => {
            clearInterval(interval);
            showError('Error: ' + error.message);
            setStatus('Ready for new upload');
        });
    }, 2000);
}

// Helper functions
function resetView() {
    scale = 1;
    translateX = 0;
    translateY = 0;
    if (loadedImage) {
        drawBoxes(allObjects);
    }
}

function setStatus(message) {
    statusDiv.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
}

function showError(message) {
    errorDiv.style.display = 'flex';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
}

function hideError() {
    errorDiv.style.display = 'none';
    errorDiv.textContent = '';
}

function handleDetectionSuccess(data) {
    setStatus('Detection complete');
    allObjects = data.detection_results[0].objects;
    initFilters(allObjects);
    drawBoxes(allObjects);
    updateObjectsCount();
    showResultsSection();
    
    // Hide overlay
    overlay.style.display = 'none';
}

function showResultsSection() {
    resultsSection.style.display = 'block';
    setTimeout(function() {
        resultsSection.classList.add('visible');
    }, 10);
}

function initFilters(objects) {
    const classes = [...new Set(objects.map(o => o.name))];
    filters = {};
    filterControls.innerHTML = '';
    
    classes.forEach(cls => {
        filters[cls] = true;
        const id = 'filter_' + cls.replace(/\s+/g, '_');
        
        const filterItem = document.createElement('div');
        filterItem.className = 'filter-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = id;
        checkbox.checked = true;
        checkbox.addEventListener('change', function() {
            filters[cls] = this.checked;
            drawBoxes(allObjects);
            updateObjectsCount();
        });
        
        const label = document.createElement('label');
        label.htmlFor = id;
        label.textContent = cls;
        
        filterItem.appendChild(checkbox);
        filterItem.appendChild(label);
        filterControls.appendChild(filterItem);
    });
}

function drawBoxes(objects) {
    // Reset transformation and clear canvas
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Apply zoom and pan
    ctx.setTransform(scale, 0, 0, scale, translateX, translateY);
    
    // Draw image
    if (loadedImage) ctx.drawImage(loadedImage, 0, 0);
    
    // Box styles
    ctx.lineWidth = 2 / scale;
    ctx.strokeStyle = '#ffffff';
    ctx.fillStyle = '#ffffff';
    ctx.font = `${Math.max(14, 16/scale)}px sans-serif`;
    
    // Clear and prepare results table
    const tableBody = document.querySelector('#detectionList');
    tableBody.innerHTML = '';
    
    objects.forEach(obj => {
        if (!filters[obj.name] || obj.confidence < minConfidence) return;
        
        const { X: cx, Y: cy, Width: w, Heigth: h, Rotation: angle } = obj;
        
        // Draw bounding box
        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(angle);
        ctx.strokeRect(-w/2, -h/2, w, h);
        
        // Draw label background
        const text = `${obj.name} ${(obj.confidence*100).toFixed(1)}%`;
        const textWidth = ctx.measureText(text).width;
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(-w/2, -h/2 - 20, textWidth + 10, 20);
        
        // Draw label text
        ctx.fillStyle = '#ffffff';
        ctx.fillText(text, -w/2 + 5, -h/2 - 5);
        ctx.restore();
        
        // Add to results table
        const row = document.createElement('tr');
        row.className = 'fade-in';
        
        row.innerHTML = `
            <td><strong>${obj.name}</strong></td>
            <td><span class="confidence-value">${(obj.confidence*100).toFixed(1)}%</span></td>
            <td>x: ${cx.toFixed(1)}, y: ${cy.toFixed(1)}</td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // Reset transformation
    ctx.setTransform(1, 0, 0, 1, 0, 0);
}

function updateObjectsCount() {
    if (!allObjects.length) {
        objectsCount.textContent = '0 objects';
        return;
    }
    
    const totalObjects = allObjects.length;
    const visibleObjects = allObjects.filter(obj => 
        filters[obj.name] && obj.confidence >= minConfidence
    ).length;
    
    objectsCount.textContent = `${visibleObjects} of ${totalObjects} objects`;
}
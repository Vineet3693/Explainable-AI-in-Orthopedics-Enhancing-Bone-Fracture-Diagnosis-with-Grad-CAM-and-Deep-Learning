/* =================================================================
   FRACTURE DETECTION AI — COMPACT UI APP LOGIC
   ================================================================= */

const API_URL = 'http://localhost:8001';

// ── DOM References ──
const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const imagesContainer = document.getElementById('imagesContainer');
const previewImg = document.getElementById('previewImg');
const gradcamBox = document.getElementById('gradcamBox');
const gradcamResultImg = document.getElementById('gradcamResultImg');
const overlayControls = document.getElementById('overlayControls');
const opacitySlider = document.getElementById('opacitySlider');

const modelSelect = document.getElementById('modelSelect');
const sensitivitySelect = document.getElementById('sensitivitySelect');
const analyzeBtn = document.getElementById('analyzeBtn');
const clearBtn = document.getElementById('clearBtn');
const explainBtn = document.getElementById('explainBtn');
const downloadBtn = document.getElementById('downloadBtn');

const apiStatusBadge = document.getElementById('apiStatusBadge');
const apiStatusText = document.getElementById('apiStatusText');
const warningBanner = document.getElementById('warningBanner');
const loader = document.getElementById('loader');
const emptyState = document.getElementById('emptyState');
const resultsContent = document.getElementById('resultsContent');

const accVal = document.getElementById('accVal'), aucVal = document.getElementById('aucVal');
const diagnosisValue = document.getElementById('diagnosisValue'), confText = document.getElementById('confText');
const confCircle = document.getElementById('confCircle'), recBox = document.getElementById('recBox');

const breakdownCard = document.getElementById('breakdownCard'), breakdownList = document.getElementById('breakdownList'), agreeBadge = document.getElementById('agreeBadge');
const aiSection = document.getElementById('aiSection'), groqBlock = document.getElementById('groqBlock'), geminiBlock = document.getElementById('geminiBlock');
const rocImg = document.getElementById('rocImg'), rocPlaceholder = document.getElementById('rocPlaceholder');

let currentFile = null;
let lastResultsData = null; // Store for PDF

// ── Init ──
checkHealth();
loadROC();

async function checkHealth() {
    try {
        const res = await fetch(`${API_URL}/health`);
        if (res.ok) {
            apiStatusBadge.className = 'api-status-badge'; apiStatusText.textContent = 'API Online';
            const modelRes = await fetch(`${API_URL}/api/v1/models`);
            const data = await modelRes.json();

            document.querySelectorAll('#modelSelect option:not([value="ensemble"])').forEach(el => el.remove());
            data.models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.name; opt.textContent = `${m.name} (${(m.accuracy * 100).toFixed(1)}% Acc)`;
                if (m.status !== 'active') opt.disabled = true;
                modelSelect.appendChild(opt);
            });
        } else throw new Error();
    } catch {
        apiStatusBadge.className = 'api-status-badge offline'; apiStatusText.textContent = 'API Offline';
    }
}

async function loadROC() {
    try {
        const res = await fetch(`${API_URL}/api/v1/roc-curve`);
        if (res.ok) { rocImg.src = `${API_URL}/api/v1/roc-curve`; rocImg.style.display = 'block'; rocPlaceholder.style.display = 'none'; }
    } catch { }
}

// ── Drag & Drop ──
dropzone.addEventListener('click', () => fileInput.click());
['dragover', 'dragleave', 'drop'].forEach(evt => dropzone.addEventListener(evt, e => e.preventDefault()));
dropzone.addEventListener('drop', e => { if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]); });
fileInput.addEventListener('change', e => { if (e.target.files.length) handleFile(e.target.files[0]); });

function handleFile(file) {
    if (!file.type.startsWith('image/')) return alert('Select an image file.');
    currentFile = file;
    const reader = new FileReader();
    reader.onload = e => {
        previewImg.src = e.target.result;
        imagesContainer.style.display = 'block';
        dropzone.style.display = 'none';
        gradcamBox.style.display = 'none';
        overlayControls.style.display = 'none';
        explainBtn.style.display = 'block';

        // Reset PDF images
        document.getElementById('pdfImgOrig').src = e.target.result;
    };
    reader.readAsDataURL(file);
    analyzeBtn.disabled = false;
    clearBtn.style.display = 'flex';
}

// ── Clear ──
clearBtn.addEventListener('click', () => {
    currentFile = null; lastResultsData = null; fileInput.value = '';
    imagesContainer.style.display = 'none'; dropzone.style.display = 'block';
    analyzeBtn.disabled = true; clearBtn.style.display = 'none';
    warningBanner.style.display = 'none'; loader.style.display = 'none';
    emptyState.style.display = 'flex'; resultsContent.style.display = 'none';
    downloadBtn.style.display = 'none';
});

opacitySlider.addEventListener('input', e => {
    // Only apply opacity if we overlayed it; in this compact UI we show GradCAM side/below, so opacity might not be needed unless using absolute mix-blend.
    // For pure image swap, we keep opacity at 1. But left it just in case.
    gradcamResultImg.style.opacity = e.target.value;
});

// ── Tabs Logic ──
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');
    });
});

// ── Analyze ──
analyzeBtn.addEventListener('click', async () => {
    if (!currentFile) return;
    emptyState.style.display = 'none'; resultsContent.style.display = 'none';
    loader.style.display = 'flex'; analyzeBtn.disabled = true; warningBanner.style.display = 'none'; downloadBtn.style.display = 'none';

    const formData = new FormData(); formData.append('file', currentFile);
    try {
        const res = await fetch(`${API_URL}/api/v1/predict?model_name=${encodeURIComponent(modelSelect.value)}&sensitivity=${sensitivitySelect.value}`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error((await res.json()).detail || 'Prediction failed');
        lastResultsData = await res.json();
        displayResults(lastResultsData);
    } catch (err) {
        alert(`Analysis Error: ${err.message}`); emptyState.style.display = 'flex';
    } finally {
        loader.style.display = 'none'; analyzeBtn.disabled = false;
    }
});

function displayResults(data) {
    resultsContent.style.display = 'flex'; downloadBtn.style.display = 'flex';
    const isFractured = data.final_result === 'Fractured';
    const theme = isFractured ? 'fractured' : 'normal';
    const confPct = Math.round(data.final_confidence * 100);

    warningBanner.style.display = confPct < 60 ? 'flex' : 'none';

    // Header updates
    diagnosisValue.textContent = data.final_result;
    diagnosisValue.className = `diagnosis-value ${theme}`;
    confText.textContent = confPct + '%';
    document.querySelector('.confidence-circle').className = `confidence-circle ${theme}`;
    setTimeout(() => { confCircle.style.strokeDashoffset = 264 - (264 * confPct / 100); }, 50);
    recBox.textContent = data.recommendation;
    recBox.className = `rec-box ${theme}`;

    // PDF Updates
    document.getElementById('pdfDiagnosis').textContent = data.final_result;
    document.getElementById('pdfDiagnosis').style.color = isFractured ? '#ef4444' : '#10b981';
    document.getElementById('pdfConf').textContent = confPct + '%';
    document.getElementById('pdfRec').textContent = data.recommendation;

    // AI Tab
    if (data.ai_analysis && !data.ai_analysis.error) {
        groqBlock.innerHTML = data.ai_analysis.summary || 'N/A';
        geminiBlock.innerHTML = data.ai_analysis.detailed || 'N/A';
        // PDF
        document.getElementById('pdfGroq').textContent = data.ai_analysis.summary || 'Summary unavailable.';
        document.getElementById('pdfGemini').textContent = data.ai_analysis.detailed || 'Detailed report unavailable.';
    }

    // Ensemble Tab
    if (data.mode === 'ensemble' && data.individual_predictions?.length > 1) {
        breakdownCard.style.display = 'block';
        agreeBadge.textContent = data.methods_agree ? 'Unanimous' : 'Mixed';
        agreeBadge.style.color = data.methods_agree ? 'var(--accent)' : 'var(--warning)';

        breakdownList.innerHTML = '';
        data.individual_predictions.forEach(p => {
            const row = document.createElement('div'); row.className = 'breakdown-item';
            row.innerHTML = `
                <div>${p.model}</div>
                <div><span class="pred-tag ${p.prediction === 'Fractured' ? 'fractured' : 'normal'}">${p.prediction}</span></div>
                <div style="color:var(--text-muted)">${Math.round(p.confidence * 100)}%</div>
            `;
            breakdownList.appendChild(row);
        });
    } else breakdownCard.style.display = 'none';

    // GradCAM Heatmap
    if (data.gradcam_image) {
        gradcamResultImg.src = `${API_URL}${data.gradcam_image}`;
        gradcamBox.style.display = 'block';
        explainBtn.style.display = 'none';
        document.getElementById('pdfImgHeatmap').src = `${API_URL}${data.gradcam_image}`;
    }
}

// ── Manual Explain ──
explainBtn.addEventListener('click', async () => {
    if (!currentFile) return;
    explainBtn.disabled = true; explainBtn.textContent = '⏳ Generating…';
    try {
        const formData = new FormData(); formData.append('file', currentFile);
        const res = await fetch(`${API_URL}/api/v1/gradcam`, { method: 'POST', body: formData });
        if (!res.ok) throw new Error('GradCAM failed');
        const url = URL.createObjectURL(await res.blob());

        gradcamResultImg.src = url;
        gradcamBox.style.display = 'block';
        explainBtn.style.display = 'none';
        document.getElementById('pdfImgHeatmap').src = url;
    } catch (err) { alert(err.message); }
    finally { explainBtn.disabled = false; explainBtn.textContent = '🔥 Generate Heatmap'; }
});

// ── PDF Download ──
downloadBtn.addEventListener('click', () => {
    if (!lastResultsData) return;
    const element = document.getElementById('pdfTemplate');
    element.style.display = 'block'; // Make visible for capture

    html2pdf().set({
        margin: 10,
        filename: `FractureReport_${Date.now()}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }).from(element).save().then(() => {
        element.style.display = 'none'; // Hide again
    });
});

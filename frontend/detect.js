/**
 * CivicAI — Detect Page Logic
 *
 * Handles:
 *  1. Image upload (file picker + drag-and-drop)
 *  2. POST /api/analyze → display AI prediction
 *  3. Category confirmation / override + description
 *  4. POST /api/reports → display report ID
 *
 * Depends on: config.js (API_BASE_URL), app.js (tr, toast, theme, lang)
 */

/* ── DOM References ──────────────────────────────────────── */
const input = document.getElementById("imageInput");
const box = document.getElementById("upload");
const preview = document.getElementById("preview");
const resultTitle = document.getElementById("resultTitle");
const resultText = document.getElementById("resultText");
const loader = document.getElementById("loader");
const reportForm = document.getElementById("reportForm");
const reportResult = document.getElementById("reportResult");
const categorySelect = document.getElementById("categorySelect");
const descriptionInput = document.getElementById("descriptionInput");
const submitBtn = document.getElementById("submitReport");

// V2 Geolocation DOM
const getLocationBtn = document.getElementById("getLocationBtn");
const locationStatus = document.getElementById("locationStatus");
const showManualLocBtn = document.getElementById("showManualLocBtn");
const manualLocationFields = document.getElementById("manualLocationFields");
const manualLat = document.getElementById("manualLat");
const manualLng = document.getElementById("manualLng");
const applyManualLocBtn = document.getElementById("applyManualLocBtn");

/* ── State ───────────────────────────────────────────────── */
let currentFile = null;      // the File object the user uploaded
let lastAiResult = null;     // the JSON response from /api/analyze
let currentLat = null;
let currentLng = null;
let currentLocSource = null;
let currentLocAccuracy = null;

/* ── Upload Handlers ─────────────────────────────────────── */
input?.addEventListener("change", () => handleImage(input.files[0]));
box?.addEventListener("dragover", e => { e.preventDefault(); box.classList.add("drag"); });
box?.addEventListener("dragleave", () => box.classList.remove("drag"));
box?.addEventListener("drop", e => {
  e.preventDefault();
  box.classList.remove("drag");
  handleImage(e.dataTransfer.files[0]);
});

function handleImage(file) {
  if (!file || !file.type.startsWith("image/")) return toast("Please select a valid image.");

  // Extension check (client-side — server also validates)
  const ext = file.name.split(".").pop().toLowerCase();
  if (!["jpg", "jpeg", "png"].includes(ext)) {
    return toast("Only JPG, JPEG, and PNG images are accepted.");
  }

  currentFile = file;
  lastAiResult = null;

  // Show preview
  preview.src = URL.createObjectURL(file);
  preview.style.display = "block";

  // Hide any previous report result
  if (reportForm) reportForm.style.display = "none";
  if (reportResult) reportResult.style.display = "none";

  // Reset location state
  currentLat = null;
  currentLng = null;
  currentLocSource = null;
  currentLocAccuracy = null;
  if (locationStatus) locationStatus.innerHTML = "";
  if (showManualLocBtn) {
    showManualLocBtn.style.display = "none";
    showManualLocBtn.textContent = "Enter Location Manually";
  }
  if (manualLocationFields) manualLocationFields.style.display = "none";
  if (manualLat) manualLat.value = "";
  if (manualLng) manualLng.value = "";

  // Show loader and start analysis
  loader.classList.add("show");
  resultTitle.textContent = tr("analysing");
  resultText.textContent = "";

  analyseImage(file);
}

/* ── AI Analysis via Backend ─────────────────────────────── */
async function analyseImage(file) {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    loader.classList.remove("show");

    if (!res.ok || !data.success) {
      resultTitle.textContent = tr("result");
      resultText.innerHTML = `<span class="muted">${data.error || "Analysis failed. Please try again."}</span>`;
      toast("Analysis failed.");
      return;
    }

    lastAiResult = data;

    if (data.ai_available && data.category) {
      const confPct = Math.round((data.confidence || 0) * 100);
      resultTitle.textContent = tr("result");
      resultText.innerHTML =
        `<b>${data.category}</b>` +
        (data.subcategory && data.subcategory !== data.category
          ? ` <span class="muted">(${data.subcategory})</span>` : "") +
        `<br><span class="muted">${data.message || ""}</span>` +
        `<div class="confidence"><div id="bar2"></div></div>` +
        `<span>${confPct}% confidence</span>`;
      setTimeout(() => {
        const bar = document.getElementById("bar2");
        if (bar) bar.style.width = confPct + "%";
      }, 50);
      toast(data.category + " detected");

      // Pre-select category in the form
      if (categorySelect) {
        for (let i = 0; i < categorySelect.options.length; i++) {
          if (categorySelect.options[i].value === data.category) {
            categorySelect.selectedIndex = i;
            break;
          }
        }
      }
    } else {
      resultTitle.textContent = tr("result");
      resultText.innerHTML =
        `<span class="muted">${data.message || "No issue detected. Please select the category manually."}</span>`;
      toast("No AI detection — select category manually.");
    }

    // Show the report form
    if (reportForm) reportForm.style.display = "block";

  } catch (err) {
    loader.classList.remove("show");
    resultTitle.textContent = tr("result");
    resultText.innerHTML =
      `<span class="muted">Could not connect to the backend. Make sure the server is running at <code>${API_BASE_URL}</code>.</span>`;
    toast("Backend connection failed.");
  }
}

/* ── Geolocation Logic ───────────────────────────────────── */
getLocationBtn?.addEventListener("click", () => {
  if (!navigator.geolocation) {
    locationStatus.innerHTML = "<span style='color:var(--error)'>Geolocation is not supported by your browser.</span>";
    showManualLocBtn.style.display = "block";
    return;
  }

  locationStatus.innerHTML = "<span class='muted'>Fetching location...</span>";
  getLocationBtn.disabled = true;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      currentLat = position.coords.latitude;
      currentLng = position.coords.longitude;
      currentLocSource = "browser_gps";
      currentLocAccuracy = position.coords.accuracy;
      
      locationStatus.innerHTML = `<span style='color:var(--success)'>✓ Location secured (${currentLat.toFixed(4)}, ${currentLng.toFixed(4)})</span>`;
      getLocationBtn.disabled = false;
      showManualLocBtn.style.display = "none";
      manualLocationFields.style.display = "none";
    },
    (error) => {
      getLocationBtn.disabled = false;
      let msg = "Location fetch failed.";
      if (error.code === error.PERMISSION_DENIED) msg = "Location permission denied.";
      else if (error.code === error.POSITION_UNAVAILABLE) msg = "Location information unavailable.";
      else if (error.code === error.TIMEOUT) msg = "Location fetch timed out.";
      
      locationStatus.innerHTML = `<span style='color:var(--error)'>✗ ${msg}</span>`;
      showManualLocBtn.style.display = "block";
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
});

showManualLocBtn?.addEventListener("click", () => {
  manualLocationFields.style.display = "flex";
  showManualLocBtn.style.display = "none";
});

applyManualLocBtn?.addEventListener("click", () => {
  const lat = parseFloat(manualLat.value);
  const lng = parseFloat(manualLng.value);
  
  if (isNaN(lat) || lat < -90 || lat > 90) return toast("Invalid Latitude (-90 to 90).");
  if (isNaN(lng) || lng < -180 || lng > 180) return toast("Invalid Longitude (-180 to 180).");
  
  currentLat = lat;
  currentLng = lng;
  currentLocSource = "manual";
  currentLocAccuracy = null;
  
  locationStatus.innerHTML = `<span style='color:var(--success)'>✓ Manual location applied (${currentLat}, ${currentLng})</span>`;
  manualLocationFields.style.display = "none";
  showManualLocBtn.style.display = "block";
  showManualLocBtn.textContent = "Edit Manual Location";
});

/* ── Report Submission ───────────────────────────────────── */
submitBtn?.addEventListener("click", async () => {
  const confirmedCategory = categorySelect?.value;
  if (!confirmedCategory) return toast("Please select an issue category.");
  if (!currentFile) return toast("Please upload an image first.");

  if (currentLat === null || currentLng === null) {
    return toast("Please provide a location before submitting.");
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "SUBMITTING…";

  const payload = {
    issue_type: confirmedCategory,
    confirmed_category: confirmedCategory,
    description: descriptionInput?.value?.trim() || "",
    image_filename: currentFile.name,
    ai_result: lastAiResult ? {
      available: lastAiResult.ai_available || false,
      category: lastAiResult.category || null,
      subcategory: lastAiResult.subcategory || null,
      confidence: lastAiResult.confidence || 0.0,
      probabilities: lastAiResult.probabilities || {},
      model: lastAiResult.model || null,
      message: lastAiResult.message || null,
    } : {
      available: false,
      category: null,
      subcategory: null,
      confidence: 0.0,
      probabilities: {},
      model: null,
      message: "AI was not used.",
    },
    location: {
      latitude: currentLat,
      longitude: currentLng,
      source: currentLocSource,
      accuracy_meters: currentLocAccuracy
    }
  };

  try {
    const res = await fetch(`${API_BASE_URL}/api/reports`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      toast(data.error || "Report submission failed.");
      submitBtn.disabled = false;
      submitBtn.textContent = "SUBMIT REPORT";
      return;
    }

    // Show success
    if (reportResult) {
      reportResult.style.display = "block";
      reportResult.innerHTML =
        `<div class="eyebrow">REPORT SUBMITTED</div>` +
        `<h3>${data.report_id}</h3>` +
        `<p>Status: <b>${(data.status || "reported").toUpperCase()}</b></p>` +
        `<p class="muted">Your civic issue has been logged. Thank you for contributing to a better city.</p>`;
    }
    if (reportForm) reportForm.style.display = "none";
    toast("Report " + data.report_id + " submitted!");

  } catch (err) {
    toast("Could not submit report. Check backend connection.");
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "SUBMIT REPORT";
  }
});

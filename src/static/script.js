/**
 * MedBot AI Healthcare Suite - Client Application
 * Dynamic symptom rendering, diagnosis submission, AI chatbot interaction, and disease directory.
 */

document.addEventListener("DOMContentLoaded", () => {
  // State management
  const state = {
    selectedSymptoms: new Set(),
    symptomCatalog: {},
    allFeatures: [],
    allDiseases: [],
    activeCategory: "all",
    searchFilter: ""
  };

  // DOM Elements
  const tabButtons = document.querySelectorAll(".nav-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");
  const symptomsAccordion = document.getElementById("symptomsAccordion");
  const categoryPillsContainer = document.getElementById("categoryPills");
  const selectionCountBadge = document.getElementById("selectionCountBadge");
  const selectedTray = document.getElementById("selectedTray");
  const selectedPillsContainer = document.getElementById("selectedPillsContainer");
  const clearAllSymptomsBtn = document.getElementById("clearAllSymptomsBtn");
  const symptomSearchInput = document.getElementById("symptomSearchInput");
  const clearSearchBtn = document.getElementById("clearSearchBtn");
  const diagnoseBtn = document.getElementById("diagnose");
  const resetCheckerBtn = document.getElementById("resetCheckerBtn");

  // Diagnosis Result DOM Elements
  const resultEmptyState = document.getElementById("resultEmptyState");
  const resultLoadingState = document.getElementById("resultLoadingState");
  const resultCard = document.getElementById("resultCard");
  const diagTitle = document.getElementById("diagTitle");
  const severityBadge = document.getElementById("severityBadge");
  const specialistBadge = document.getElementById("specialistBadge");
  const gaugeValue = document.getElementById("gaugeValue");
  const diagMatchedSymptoms = document.getElementById("diagMatchedSymptoms");
  const diagDescription = document.getElementById("diagDescription");
  const differentialsList = document.getElementById("differentialsList");
  const precautionsList = document.getElementById("precautionsList");
  const redFlagsBox = document.getElementById("redFlagsBox");
  const redFlagsText = document.getElementById("redFlagsText");

  // Chat DOM Elements
  const chatMessages = document.getElementById("chatMessages");
  const chatInput = document.getElementById("chatInput");
  const chatSendBtn = document.getElementById("chatSendBtn");
  const clearChatBtn = document.getElementById("clearChatBtn");

  // Library DOM Elements
  const diseaseGrid = document.getElementById("diseaseGrid");
  const librarySearchInput = document.getElementById("librarySearchInput");
  const diseaseCountSpan = document.getElementById("diseaseCount");

  // =========================================================================
  // 1. Tab Switching
  // =========================================================================
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const tabId = btn.getAttribute("data-tab");
      tabButtons.forEach(b => {
        b.classList.remove("active");
        b.setAttribute("aria-selected", "false");
      });
      tabPanes.forEach(p => (p.style.display = "none"));

      btn.classList.add("active");
      btn.setAttribute("aria-selected", "true");
      const targetPane = document.getElementById(`tab-${tabId}`);
      if (targetPane) targetPane.style.display = "block";
    });
  });

  // =========================================================================
  // 2. Fetch and Render Symptoms
  // =========================================================================
  async function loadSymptoms() {
    try {
      const res = await fetch("/api/symptoms");
      if (!res.ok) throw new Error("Could not load symptom catalog.");
      const data = await res.json();
      state.symptomCatalog = data.categories || {};
      state.allFeatures = data.all_features || [];

      renderCategoryPills();
      renderSymptomsGrid();
    } catch (err) {
      console.error(err);
      symptomsAccordion.innerHTML = `
        <div class="loading-spinner-box" style="color:#ef4444;">
          <p>Error loading symptoms: ${err.message}</p>
          <button class="btn btn-small btn-secondary" onclick="location.reload()">Retry</button>
        </div>`;
    }
  }

  function renderCategoryPills() {
    categoryPillsContainer.innerHTML = '<button class="cat-pill active" data-cat="all">All Systems</button>';
    Object.keys(state.symptomCatalog).forEach(cat => {
      const pill = document.createElement("button");
      pill.className = "cat-pill";
      pill.setAttribute("data-cat", cat);
      pill.textContent = cat;
      pill.addEventListener("click", () => {
        document.querySelectorAll(".cat-pill").forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        state.activeCategory = cat;
        renderSymptomsGrid();
      });
      categoryPillsContainer.appendChild(pill);
    });

    categoryPillsContainer.querySelector('[data-cat="all"]').addEventListener("click", (e) => {
      document.querySelectorAll(".cat-pill").forEach(p => p.classList.remove("active"));
      e.target.classList.add("active");
      state.activeCategory = "all";
      renderSymptomsGrid();
    });
  }

  function renderSymptomsGrid() {
    symptomsAccordion.innerHTML = "";
    const filter = state.searchFilter.toLowerCase().trim();
    let totalVisible = 0;

    Object.entries(state.symptomCatalog).forEach(([catName, symptoms]) => {
      if (state.activeCategory !== "all" && state.activeCategory !== catName) {
        return;
      }

      // Filter by search string
      const matched = symptoms.filter(s => {
        if (!filter) return true;
        return (
          s.label.toLowerCase().includes(filter) ||
          s.id.toLowerCase().includes(filter) ||
          (s.desc && s.desc.toLowerCase().includes(filter))
        );
      });

      if (matched.length === 0) return;
      totalVisible += matched.length;

      const groupDiv = document.createElement("div");
      groupDiv.className = "symptoms-category-group";

      const title = document.createElement("div");
      title.className = "category-group-title";
      title.textContent = `${catName} (${matched.length})`;
      groupDiv.appendChild(title);

      const grid = document.createElement("div");
      grid.className = "symptom-items-grid";

      matched.forEach(item => {
        const isChecked = state.selectedSymptoms.has(item.id);
        const card = document.createElement("div");
        card.className = `symptom-item ${isChecked ? "checked" : ""}`;
        card.innerHTML = `
          <input type="checkbox" class="symptom-checkbox" value="${item.id}" ${isChecked ? "checked" : ""} />
          <div class="symptom-info">
            <span class="symptom-name">${item.label}</span>
            <span class="symptom-desc">${item.desc || ""}</span>
          </div>
        `;

        card.addEventListener("click", (e) => {
          // Prevent double toggle if checkbox clicked directly
          if (e.target.tagName !== "INPUT") {
            const cb = card.querySelector(".symptom-checkbox");
            cb.checked = !cb.checked;
          }
          toggleSymptom(item.id, card.querySelector(".symptom-checkbox").checked);
        });

        grid.appendChild(card);
      });

      groupDiv.appendChild(grid);
      symptomsAccordion.appendChild(groupDiv);
    });

    if (totalVisible === 0) {
      symptomsAccordion.innerHTML = `
        <div class="loading-spinner-box">
          <p>No symptoms matching "${state.searchFilter}".</p>
        </div>`;
    }
  }

  function toggleSymptom(id, isSelected) {
    if (isSelected) {
      state.selectedSymptoms.add(id);
    } else {
      state.selectedSymptoms.delete(id);
    }
    updateSelectionUI();
  }

  function updateSelectionUI() {
    const count = state.selectedSymptoms.size;
    selectionCountBadge.textContent = `${count} selected`;

    // Update Tray
    if (count > 0) {
      selectedTray.style.display = "block";
      selectedPillsContainer.innerHTML = "";
      state.selectedSymptoms.forEach(id => {
        // Find label
        let label = id.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        for (const cat of Object.values(state.symptomCatalog)) {
          const found = cat.find(s => s.id === id);
          if (found) { label = found.label; break; }
        }

        const pill = document.createElement("div");
        pill.className = "selected-pill";
        pill.innerHTML = `
          <span>${label}</span>
          <button class="selected-pill-remove" title="Remove">&times;</button>
        `;
        pill.querySelector(".selected-pill-remove").addEventListener("click", () => {
          state.selectedSymptoms.delete(id);
          updateSelectionUI();
          renderSymptomsGrid();
        });
        selectedPillsContainer.appendChild(pill);
      });
    } else {
      selectedTray.style.display = "none";
    }

    // Refresh checkbox states in grid
    document.querySelectorAll(".symptom-item").forEach(card => {
      const cb = card.querySelector(".symptom-checkbox");
      if (cb) {
        const isChecked = state.selectedSymptoms.has(cb.value);
        cb.checked = isChecked;
        if (isChecked) card.classList.add("checked");
        else card.classList.remove("checked");
      }
    });
  }

  // Search input listeners
  symptomSearchInput.addEventListener("input", (e) => {
    state.searchFilter = e.target.value;
    clearSearchBtn.style.display = state.searchFilter ? "block" : "none";
    renderSymptomsGrid();
  });

  clearSearchBtn.addEventListener("click", () => {
    symptomSearchInput.value = "";
    state.searchFilter = "";
    clearSearchBtn.style.display = "none";
    renderSymptomsGrid();
  });

  clearAllSymptomsBtn.addEventListener("click", () => {
    state.selectedSymptoms.clear();
    updateSelectionUI();
    renderSymptomsGrid();
  });

  resetCheckerBtn.addEventListener("click", () => {
    state.selectedSymptoms.clear();
    updateSelectionUI();
    renderSymptomsGrid();
    resultCard.style.display = "none";
    resultLoadingState.style.display = "none";
    resultEmptyState.style.display = "block";
  });

  // Quick Preset Chips
  document.querySelectorAll(".quick-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const symList = chip.getAttribute("data-symptoms").split(",");
      state.selectedSymptoms.clear();
      symList.forEach(s => state.selectedSymptoms.add(s.trim()));
      updateSelectionUI();
      renderSymptomsGrid();
      runDiagnosis();
    });
  });

  // =========================================================================
  // 3. Clinical Diagnosis Prediction
  // =========================================================================
  diagnoseBtn.addEventListener("click", runDiagnosis);

  async function runDiagnosis() {
    const symptoms = Array.from(state.selectedSymptoms);
    if (symptoms.length === 0) {
      alert("Please select at least one symptom before running diagnosis.");
      return;
    }

    resultEmptyState.style.display = "none";
    resultCard.style.display = "none";
    resultLoadingState.style.display = "block";

    try {
      const res = await fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms })
      });

      const data = await res.json();
      resultLoadingState.style.display = "none";

      if (!res.ok || data.error) {
        alert(data.error || "Prediction request failed.");
        resultEmptyState.style.display = "block";
        return;
      }

      renderDiagnosisCard(data);
    } catch (err) {
      resultLoadingState.style.display = "none";
      resultEmptyState.style.display = "block";
      alert("Network error: " + err.message);
    }
  }

  function renderDiagnosisCard(data) {
    resultCard.style.display = "block";
    diagTitle.textContent = data.diagnosis;
    gaugeValue.textContent = `${data.confidence}%`;

    // Severity Badge Class
    const sev = (data.severity || "Moderate").toLowerCase();
    severityBadge.textContent = data.severity || "Moderate";
    severityBadge.className = "severity-badge";
    if (sev.includes("emergency")) severityBadge.classList.add("emergency");
    else if (sev.includes("high") || sev.includes("urgent")) severityBadge.classList.add("high");
    else if (sev.includes("mild")) severityBadge.classList.add("mild");
    else severityBadge.classList.add("moderate");

    specialistBadge.textContent = data.specialist || "General Physician";
    diagDescription.textContent = data.description || "Medical evaluation indicated.";

    // Matched Symptoms
    diagMatchedSymptoms.innerHTML = "";
    (data.matched_symptoms || []).forEach(sym => {
      const pill = document.createElement("span");
      pill.className = "matched-pill";
      pill.textContent = sym;
      diagMatchedSymptoms.appendChild(pill);
    });

    // Differential Diagnoses
    differentialsList.innerHTML = "";
    (data.differentials || []).forEach(diff => {
      const row = document.createElement("div");
      row.className = "diff-row";
      row.innerHTML = `
        <div class="diff-info">
          <span>${diff.disease}</span>
          <span>${diff.confidence}%</span>
        </div>
        <div class="diff-bar-container">
          <div class="diff-bar-fill" style="width: ${Math.min(diff.confidence, 100)}%;"></div>
        </div>
      `;
      differentialsList.appendChild(row);
    });

    // Precautions
    precautionsList.innerHTML = "";
    (data.precautions || []).forEach(item => {
      const li = document.createElement("li");
      li.textContent = item;
      precautionsList.appendChild(li);
    });

    // Red Flags
    if (data.red_flags) {
      redFlagsBox.style.display = "block";
      redFlagsText.textContent = data.red_flags;
    } else {
      redFlagsBox.style.display = "none";
    }

    // Scroll into view on mobile
    if (window.innerWidth < 960) {
      resultCard.scrollIntoView({ behavior: "smooth" });
    }
  }

  // =========================================================================
  // 4. Conversational AI Doctor Chat
  // =========================================================================
  chatSendBtn.addEventListener("click", sendChatMessage);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  });

  clearChatBtn.addEventListener("click", () => {
    chatMessages.innerHTML = `
      <div class="message bot-message">
        <div class="msg-avatar">🤖</div>
        <div class="msg-bubble">
          <p>Chat cleared. What symptoms would you like to discuss?</p>
        </div>
      </div>
    `;
  });

  // Suggestion prompt chips in chat
  document.querySelectorAll(".chat-prompt-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      chatInput.value = chip.getAttribute("data-prompt");
      sendChatMessage();
    });
  });

  async function sendChatMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Append User Message
    appendMessage("user", text);
    chatInput.value = "";

    // Show bot typing placeholder
    const typingId = appendTypingIndicator();

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text })
      });
      const data = await res.json();
      removeTypingIndicator(typingId);

      if (data.error) {
        appendMessage("bot", `I encountered an issue: ${data.error}`);
        return;
      }

      // Append Bot Response
      let botHtml = `<p>${formatMarkdown(data.reply)}</p>`;

      if (data.diagnosis_available && data.details) {
        const d = data.details;
        botHtml += `
          <div class="chat-diagnosis-preview">
            <div style="font-weight:700; color:#0284c7; font-size:0.85rem; margin-bottom:0.3rem;">
              🔬 Primary Prediction: <strong>${d.diagnosis}</strong> (${d.confidence}%)
            </div>
            <div style="font-size:0.8rem; margin-bottom:0.4rem;">
              <strong>Severity:</strong> ${d.severity} | <strong>Specialist:</strong> ${d.specialist}
            </div>
            <div style="font-size:0.8rem; color:#475569; margin-bottom:0.4rem;">
              ${d.description}
            </div>
            <div style="font-size:0.78rem; font-weight:600; color:#334155; margin-top:0.4rem;">Key Recommendations:</div>
            <ul style="font-size:0.78rem; padding-left:1.1rem; margin-top:0.2rem; color:#475569;">
              ${(d.precautions || []).map(p => `<li>${p}</li>`).join("")}
            </ul>
          </div>
        `;
      }

      appendMessage("bot", botHtml, true);
    } catch (err) {
      removeTypingIndicator(typingId);
      appendMessage("bot", "Network error. Please make sure the MedBot backend is active.");
    }
  }

  function appendMessage(sender, text, isHtml = false) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}-message`;
    msgDiv.innerHTML = `
      <div class="msg-avatar">${sender === "bot" ? "🤖" : "👤"}</div>
      <div class="msg-bubble">${isHtml ? text : `<p>${escapeHtml(text)}</p>`}</div>
    `;
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  function appendTypingIndicator() {
    const id = "typing-" + Date.now();
    const typingDiv = document.createElement("div");
    typingDiv.id = id;
    typingDiv.className = "message bot-message";
    typingDiv.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-bubble" style="display:flex; align-items:center; gap:0.4rem; padding:0.6rem 0.9rem;">
        <span class="status-dot"></span>
        <span style="font-size:0.8rem; color:#64748b;">MedBot is analyzing symptoms...</span>
      </div>
    `;
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  // =========================================================================
  // 5. Medical Diseases Directory Tab
  // =========================================================================
  async function loadDiseasesDirectory() {
    try {
      const res = await fetch("/api/diseases");
      if (!res.ok) throw new Error("Could not load diseases catalog.");
      const data = await res.json();
      state.allDiseases = data.diseases || [];
      if (diseaseCountSpan) diseaseCountSpan.textContent = `${data.total.toLocaleString()}+`;
      renderDiseasesGrid(state.allDiseases);
    } catch (err) {
      diseaseGrid.innerHTML = `
        <div class="loading-spinner-box" style="color:#ef4444;">
          <p>Failed to load diseases directory: ${err.message}</p>
        </div>`;
    }
  }

  function renderDiseasesGrid(list) {
    diseaseGrid.innerHTML = "";
    if (list.length === 0) {
      diseaseGrid.innerHTML = '<div class="loading-spinner-box"><p>No conditions found.</p></div>';
      return;
    }

    list.forEach(name => {
      const card = document.createElement("div");
      card.className = "disease-badge-card";
      card.innerHTML = `
        <span class="disease-badge-icon">🗂️</span>
        <span>${escapeHtml(name)}</span>
      `;
      diseaseGrid.appendChild(card);
    });
  }

  librarySearchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderDiseasesGrid(state.allDiseases);
    } else {
      const filtered = state.allDiseases.filter(d => d.toLowerCase().includes(q));
      renderDiseasesGrid(filtered);
    }
  });

  // Utilities
  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function formatMarkdown(str) {
    return escapeHtml(str)
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>");
  }

  // Initial Boot
  loadSymptoms();
  loadDiseasesDirectory();
});
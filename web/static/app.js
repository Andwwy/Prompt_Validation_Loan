/**
 * Interactive Client Application for Fair Housing & Lending Prompt Validator
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const promptInput = document.getElementById('promptInput');
  const charCounter = document.getElementById('charCounter');
  const presetSelect = document.getElementById('presetSelect');
  const contextSelect = document.getElementById('contextSelect');
  const semanticToggle = document.getElementById('semanticToggle');
  const semanticToggleLabel = document.getElementById('semanticToggleLabel');
  const validateBtn = document.getElementById('validateBtn');
  const clearPromptBtn = document.getElementById('clearPromptBtn');

  // Result UI Elements
  const emptyState = document.getElementById('emptyState');
  const loadingState = document.getElementById('loadingState');
  const resultContent = document.getElementById('resultContent');
  const statusBadgeContainer = document.getElementById('statusBadgeContainer');
  const riskScoreValue = document.getElementById('riskScoreValue');
  const severityBadge = document.getElementById('severityBadge');
  const riskProgressBar = document.getElementById('riskProgressBar');
  const resultSummaryText = document.getElementById('resultSummaryText');
  const violationsSection = document.getElementById('violationsSection');
  const violationsList = document.getElementById('violationsList');
  const violationCountBadge = document.getElementById('violationCountBadge');
  const rewriteSection = document.getElementById('rewriteSection');
  const rewriteText = document.getElementById('rewriteText');
  const copyRewriteBtn = document.getElementById('copyRewriteBtn');
  const applyRewriteBtn = document.getElementById('applyRewriteBtn');

  const execTimeText = document.getElementById('execTimeText');
  const checksRunText = document.getElementById('checksRunText');
  const semanticAiStatus = document.getElementById('semanticAiStatus');

  // Modals
  const apiKeyBtn = document.getElementById('apiKeyBtn');
  const apiKeyModal = document.getElementById('apiKeyModal');
  const closeApiKeyModal = document.getElementById('closeApiKeyModal');
  const cancelApiKeyBtn = document.getElementById('cancelApiKeyBtn');
  const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const keyFeedback = document.getElementById('keyFeedback');
  const apiKeyStatusText = document.getElementById('apiKeyStatusText');

  const legalRefBtn = document.getElementById('legalRefBtn');
  const legalModal = document.getElementById('legalModal');
  const closeLegalModal = document.getElementById('closeLegalModal');
  const legalStatutesContainer = document.getElementById('legalStatutesContainer');

  let benchmarkCases = [];
  let userApiKey = localStorage.getItem('gemini_api_key') || '';

  // 1. Initial State & Health Check
  async function checkHealth() {
    try {
      const res = await fetch('/api/health');
      const data = await res.json();
      updateApiKeyStatus(data.gemini_configured || !!userApiKey);
    } catch (e) {
      console.warn('Health check failed:', e);
    }
  }

  function updateApiKeyStatus(hasKey) {
    if (hasKey) {
      apiKeyStatusText.textContent = 'Gemini AI: Connected';
      semanticToggleLabel.textContent = 'Gemini Semantic AI (Active)';
      semanticAiStatus.textContent = 'Active (Gemini 2.5)';
      apiKeyBtn.classList.remove('btn-secondary');
      apiKeyBtn.classList.add('btn-accent');
    } else {
      apiKeyStatusText.textContent = 'Add Gemini Key';
      semanticToggleLabel.textContent = 'Gemini Semantic AI (Key Needed)';
      semanticAiStatus.textContent = 'Offline (Rules Only)';
      apiKeyBtn.classList.add('btn-secondary');
      apiKeyBtn.classList.remove('btn-accent');
    }
  }

  // 2. Load Benchmarks
  async function loadBenchmarks() {
    try {
      const res = await fetch('/api/benchmarks');
      benchmarkCases = await res.json();

      benchmarkCases.forEach((c) => {
        const opt = document.createElement('option');
        opt.value = c.id;
        const icon = c.expected_compliant ? '✅' : '⚠️';
        opt.textContent = `${icon} ${c.id}: ${c.prompt.substring(0, 55)}...`;
        presetSelect.appendChild(opt);
      });
    } catch (e) {
      console.error('Failed to load benchmarks:', e);
    }
  }

  // 3. Preset Selection
  presetSelect.addEventListener('change', () => {
    const selectedId = presetSelect.value;
    if (!selectedId) return;
    const found = benchmarkCases.find((c) => c.id === selectedId);
    if (found) {
      promptInput.value = found.prompt;
      updateCharCounter();
      runValidation();
    }
  });

  // Quick Pills
  document.querySelectorAll('.pill-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const presetId = btn.getAttribute('data-preset');
      const found = benchmarkCases.find((c) => c.id === presetId);
      if (found) {
        presetSelect.value = found.id;
        promptInput.value = found.prompt;
        updateCharCounter();
        runValidation();
      }
    });
  });

  // 4. Character Counter
  function updateCharCounter() {
    const len = promptInput.value.length;
    charCounter.textContent = `${len} character${len === 1 ? '' : 's'}`;
  }
  promptInput.addEventListener('input', updateCharCounter);

  clearPromptBtn.addEventListener('click', () => {
    promptInput.value = '';
    presetSelect.value = '';
    updateCharCounter();
    promptInput.focus();
  });

  // Ctrl+Enter shortcut
  promptInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      runValidation();
    }
  });

  // 5. Validation Execution
  async function runValidation() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      promptInput.focus();
      return;
    }

    // Show loading state
    emptyState.classList.add('hidden');
    resultContent.classList.add('hidden');
    loadingState.classList.remove('hidden');
    validateBtn.disabled = true;

    try {
      const payload = {
        prompt: prompt,
        context: contextSelect.value,
        enable_semantic_analysis: semanticToggle.checked,
        api_key: userApiKey || null
      };

      const res = await fetch('/api/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Validation failed with status ${res.status}`);
      }

      const result = await res.json();
      renderResults(result);
    } catch (err) {
      console.error(err);
      alert('Validation error: ' + err.message);
    } finally {
      loadingState.classList.add('hidden');
      validateBtn.disabled = false;
    }
  }

  validateBtn.addEventListener('click', runValidation);

  // 6. Render Results
  function renderResults(res) {
    resultContent.classList.remove('hidden');

    // Risk Meter & Status
    const isCompliant = res.is_compliant;
    const score = res.risk_score;

    riskScoreValue.innerHTML = `${score.toFixed(2)} <span class="score-scale">/ 1.00</span>`;
    riskProgressBar.style.width = `${Math.max(score * 100, 2)}%`;

    if (isCompliant) {
      statusBadgeContainer.innerHTML = `<span class="badge badge-success">COMPLIANT</span>`;
      severityBadge.className = 'badge badge-success';
      severityBadge.textContent = 'CLEAN';
      riskProgressBar.style.backgroundColor = 'var(--color-success)';
    } else {
      const sev = res.overall_severity || 'HIGH';
      if (sev === 'CRITICAL') {
        statusBadgeContainer.innerHTML = `<span class="badge badge-danger">CRITICAL VIOLATION</span>`;
        severityBadge.className = 'badge badge-danger';
        severityBadge.textContent = 'CRITICAL RISK';
        riskProgressBar.style.backgroundColor = 'var(--color-danger)';
      } else if (sev === 'HIGH') {
        statusBadgeContainer.innerHTML = `<span class="badge badge-warning">HIGH RISK VIOLATION</span>`;
        severityBadge.className = 'badge badge-warning';
        severityBadge.textContent = 'HIGH RISK';
        riskProgressBar.style.backgroundColor = 'var(--color-warning)';
      } else {
        statusBadgeContainer.innerHTML = `<span class="badge badge-warning">MODERATE RISK</span>`;
        severityBadge.className = 'badge badge-warning';
        severityBadge.textContent = 'MODERATE';
        riskProgressBar.style.backgroundColor = 'var(--color-warning)';
      }
    }

    resultSummaryText.textContent = res.summary;

    // Violations List
    if (!isCompliant && res.violations && res.violations.length > 0) {
      violationsSection.classList.remove('hidden');
      violationCountBadge.textContent = res.violations.length;
      violationsList.innerHTML = '';

      res.violations.forEach((v) => {
        const vCard = document.createElement('div');
        vCard.className = 'violation-card';
        vCard.innerHTML = `
          <div class="violation-top">
            <span class="violation-cat">${escapeHtml(v.category)}</span>
            <div class="violation-meta">
              <span class="badge badge-neutral">${escapeHtml(v.protected_variable)}</span>
              <span class="badge ${v.severity === 'CRITICAL' ? 'badge-danger' : 'badge-warning'}">${escapeHtml(v.severity)}</span>
            </div>
          </div>
          <div class="violation-law">Statute: <strong>${escapeHtml(v.law_cited)}</strong> (${escapeHtml(v.statutory_reference)})</div>
          ${v.flagged_text ? `<div class="violation-flagged">Flagged text: "${escapeHtml(v.flagged_text)}"</div>` : ''}
          <div class="violation-expl">${escapeHtml(v.explanation)}</div>
          <div class="violation-remed">
            <span class="remed-label">Statutory Remediation:</span> ${escapeHtml(v.remediation_guidance)}
          </div>
        `;
        violationsList.appendChild(vCard);
      });
    } else {
      violationsSection.classList.add('hidden');
    }

    // Compliant Rewrite
    if (!isCompliant && res.suggested_compliant_prompt) {
      rewriteSection.classList.remove('hidden');
      rewriteText.textContent = res.suggested_compliant_prompt;
    } else {
      rewriteSection.classList.add('hidden');
    }

    // Metadata
    if (res.audit_metadata) {
      execTimeText.textContent = `${res.audit_metadata.execution_time_ms || 0} ms`;
      checksRunText.textContent = (res.audit_metadata.checks_performed || []).join(', ');
      semanticAiStatus.textContent = res.audit_metadata.semantic_evaluator_active ? 'Active (Gemini)' : 'Offline (Rule Engine)';
    }
  }

  // Copy Rewrite
  copyRewriteBtn.addEventListener('click', () => {
    const text = rewriteText.textContent;
    navigator.clipboard.writeText(text).then(() => {
      const originalText = copyRewriteBtn.innerHTML;
      copyRewriteBtn.innerHTML = '<span>✅</span> Copied!';
      setTimeout(() => {
        copyRewriteBtn.innerHTML = originalText;
      }, 1500);
    });
  });

  // Apply Rewrite to Input
  applyRewriteBtn.addEventListener('click', () => {
    promptInput.value = rewriteText.textContent;
    updateCharCounter();
    runValidation();
  });

  // 7. Modal Handlers: API Key
  apiKeyBtn.addEventListener('click', () => {
    apiKeyInput.value = userApiKey;
    keyFeedback.classList.add('hidden');
    apiKeyModal.classList.remove('hidden');
    apiKeyInput.focus();
  });

  closeApiKeyModal.addEventListener('click', () => apiKeyModal.classList.add('hidden'));
  cancelApiKeyBtn.addEventListener('click', () => apiKeyModal.classList.add('hidden'));

  saveApiKeyBtn.addEventListener('click', async () => {
    const key = apiKeyInput.value.trim();
    if (!key) {
      keyFeedback.className = 'feedback-msg feedback-error';
      keyFeedback.textContent = 'Please enter a valid Gemini API key.';
      keyFeedback.classList.remove('hidden');
      return;
    }

    saveApiKeyBtn.disabled = true;
    try {
      const res = await fetch('/api/configure-key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();
      if (res.ok) {
        userApiKey = key;
        localStorage.setItem('gemini_api_key', key);
        updateApiKeyStatus(true);
        keyFeedback.className = 'feedback-msg feedback-success';
        keyFeedback.textContent = 'API Key successfully configured and connected!';
        keyFeedback.classList.remove('hidden');
        setTimeout(() => apiKeyModal.classList.add('hidden'), 1000);
      } else {
        throw new Error(data.detail || 'Failed to configure key');
      }
    } catch (e) {
      keyFeedback.className = 'feedback-msg feedback-error';
      keyFeedback.textContent = 'Connection error: ' + e.message;
      keyFeedback.classList.remove('hidden');
    } finally {
      saveApiKeyBtn.disabled = false;
    }
  });

  // 8. Modal Handlers: Legal Reference
  legalRefBtn.addEventListener('click', async () => {
    legalModal.classList.remove('hidden');
    if (legalStatutesContainer.children.length === 0) {
      try {
        const res = await fetch('/api/statutes');
        const data = await res.json();
        renderLegalGuide(data);
      } catch (e) {
        legalStatutesContainer.innerHTML = '<p>Error loading legal guide.</p>';
      }
    }
  });

  closeLegalModal.addEventListener('click', () => legalModal.classList.add('hidden'));

  function renderLegalGuide(data) {
    legalStatutesContainer.innerHTML = '';
    const statutes = data.statutes || {};

    for (const [key, item] of Object.entries(statutes)) {
      if (key === 'LANDMARK_PRECEDENTS') {
        for (const [pKey, precedent] of Object.entries(item)) {
          const card = document.createElement('div');
          card.className = 'statute-card';
          card.innerHTML = `
            <div class="statute-title">
              <span>⚖️ ${escapeHtml(precedent.case)}</span>
              <span class="badge badge-neutral">Precedent</span>
            </div>
            <div class="statute-desc">${escapeHtml(precedent.principle)}</div>
          `;
          legalStatutesContainer.appendChild(card);
        }
      } else if (key === 'HUD_ADMIN_GUIDANCE') {
        for (const [gKey, guidance] of Object.entries(item)) {
          const card = document.createElement('div');
          card.className = 'statute-card';
          card.innerHTML = `
            <div class="statute-title">
              <span>📋 ${escapeHtml(guidance.title)}</span>
              <span class="badge badge-warning">HUD Guidance</span>
            </div>
            <div class="statute-desc">${escapeHtml(guidance.rule)}</div>
          `;
          legalStatutesContainer.appendChild(card);
        }
      } else {
        const card = document.createElement('div');
        card.className = 'statute-card';
        card.innerHTML = `
          <div class="statute-title">
            <span>📜 ${escapeHtml(item.title)}</span>
            <span class="statute-cite">${escapeHtml(item.citation)}</span>
          </div>
          <div class="statute-desc">${escapeHtml(item.description || '')}</div>
        `;
        legalStatutesContainer.appendChild(card);
      }
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Init
  checkHealth();
  loadBenchmarks();
});

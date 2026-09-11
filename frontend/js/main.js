import { fetchStations, fetchSinglePrediction, fetchForecast } from './api.js';
import { renderMainChart } from './charts.js';
import {
  elements,
  today,
  populateHourSelect,
  switchTab,
  updateNetworkPulse,
  renderStationCards,
  closeModal,
  currentModalStation,
  renderCheckResult,
  renderPlanTable,
  renderPlanKPIs
} from './ui.js';

let allStations = [];

document.addEventListener('DOMContentLoaded', async () => {
  // Initialize Defaults
  elements.ckDate.value = today();
  elements.plDate.value = today();
  populateHourSelect(elements.ckHour);

  // Setup Tabs
  elements.navTabs.forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  // Setup Search and Sort
  elements.searchInput.addEventListener('input', applyFilterAndSort);
  elements.sortSelect.addEventListener('change', applyFilterAndSort);

  // Setup Modal Listeners
  elements.btnModalClose.addEventListener('click', closeModal);
  elements.modal.addEventListener('click', e => {
    if (e.target === elements.modal) closeModal();
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !elements.modal.classList.contains('hidden')) closeModal();
  });

  elements.btnModalCheck.addEventListener('click', () => {
    if (!currentModalStation) return;
    elements.ckStation.value = currentModalStation.name;
    elements.plStation.value = currentModalStation.name;
    closeModal();
    switchTab('check-view');
    elements.checkForm.dispatchEvent(new Event('submit'));
  });

  // Setup Forms
  elements.checkForm.addEventListener('submit', handleCheckSubmit);
  elements.planForm.addEventListener('submit', handlePlanSubmit);

  // Initial Data Load
  await loadStations();
});

async function loadStations() {
  const btn = document.getElementById('btn-check');
  if (btn) btn.textContent = 'Loading…';

  const populateSelectors = (stations) => {
    [elements.ckStation, elements.plStation].forEach(sel => {
      sel.innerHTML = '';
      stations.forEach(s => sel.add(new Option(s.name, s.name)));
    });

    const maj = stations.find(s => s.name.includes('Majestic'));
    if (maj) {
      elements.ckStation.value = maj.name;
      elements.plStation.value = maj.name;
    }
  };

  try {
    const data = await fetchStations();
    allStations = data.stations;
    populateSelectors(allStations);
    updateNetworkPulse(allStations);
    applyFilterAndSort();

    // Auto-run initial prediction for instant dashboard data
    elements.checkForm.dispatchEvent(new Event('submit'));
  } catch (err) {
    console.warn("Initial station load failed. Retrying in 2s...", err);
    setTimeout(async () => {
      try {
        const data = await fetchStations();
        allStations = data.stations;
        populateSelectors(allStations);
        updateNetworkPulse(allStations);
        applyFilterAndSort();
        elements.checkForm.dispatchEvent(new Event('submit'));
      } catch (e) {
        console.error("Backend unreachable.", e);
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Check';
        }
        if (elements.stationGrid) {
          elements.stationGrid.innerHTML = `
            <div class="empty-state" style="color: #991b1b; background: #fef2f2; padding: 1.5rem; border-radius: 8px; border: 1px solid #fecaca;">
              <strong>⚠️ Unable to connect to backend server</strong><br>
              <span style="font-size: 12px; color: #64748b;">Make sure the FastAPI server is running on http://localhost:8000</span>
            </div>
          `;
        }
      }
    }, 2000);
  }
}

function applyFilterAndSort() {
  const q = elements.searchInput.value.toLowerCase().trim();
  const sortBy = elements.sortSelect.value;

  let filtered = allStations.filter(s => s.name.toLowerCase().includes(q));

  if (sortBy === 'traffic-desc') {
    filtered.sort((a, b) => b.avg_hourly_traffic - a.avg_hourly_traffic);
  } else if (sortBy === 'traffic-asc') {
    filtered.sort((a, b) => a.avg_hourly_traffic - b.avg_hourly_traffic);
  } else if (sortBy === 'name-asc') {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  }

  renderStationCards(filtered, sortBy);
}

async function handleCheckSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-check');
  btn.disabled = true;
  btn.textContent = 'Checking…';

  try {
    const data = await fetchSinglePrediction(
      elements.ckStation.value,
      elements.ckDate.value,
      elements.ckHour.value
    );
    renderCheckResult(data);
  } catch (err) {
    console.error("Prediction error:", err);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Check';
  }
}

async function handlePlanSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('btn-plan');
  const lbl = btn.querySelector('.btn-label') || btn;
  const originalText = lbl.textContent;
  lbl.textContent = 'Forecasting…';
  btn.disabled = true;

  try {
    const data = await fetchForecast(elements.plStation.value, elements.plDate.value);
    renderPlanKPIs(data, allStations);
    renderMainChart(data);
    renderPlanTable(data);
  } catch (err) {
    console.error("Forecast error:", err);
  } finally {
    lbl.textContent = originalText;
    btn.disabled = false;
  }
}

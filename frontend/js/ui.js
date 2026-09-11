import { fetchForecast } from './api.js';
import { renderModalChart, destroyModalChart } from './charts.js';

export const elements = {
  navTabs: document.querySelectorAll('.nav-tab'),
  views: document.querySelectorAll('.view'),
  ckStation: document.getElementById('ck-station'),
  ckDate: document.getElementById('ck-date'),
  ckHour: document.getElementById('ck-hour'),
  checkForm: document.getElementById('check-form'),
  plStation: document.getElementById('pl-station'),
  plDate: document.getElementById('pl-date'),
  planForm: document.getElementById('plan-form'),
  searchInput: document.getElementById('station-search'),
  sortSelect: document.getElementById('station-sort'),
  stationGrid: document.getElementById('station-grid'),
  npTitle: document.getElementById('np-title'),
  npSubtitle: document.getElementById('np-subtitle'),
  npStationCount: document.getElementById('np-station-count'),
  npTopHub: document.getElementById('np-top-hub'),
  npRushHours: document.getElementById('np-rush-hours'),
  modal: document.getElementById('station-modal'),
  btnModalClose: document.getElementById('btn-modal-close'),
  btnModalCheck: document.getElementById('btn-modal-check'),
  mName: document.getElementById('m-name'),
  mTier: document.getElementById('m-tier'),
  mStatusBox: document.getElementById('m-status-box'),
  mEmoji: document.getElementById('m-emoji'),
  mHeadline: document.getElementById('m-headline'),
  mSubtext: document.getElementById('m-subtext'),
  mAvg: document.getElementById('m-avg'),
  mPeak: document.getElementById('m-peak'),
  mDaily: document.getElementById('m-daily')
};

export let currentModalStation = null;

export function today() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

export function formatHour(h) {
  if (h === 0)  return '12:00 AM';
  if (h < 12)   return `${String(h).padStart(2,'0')}:00 AM`;
  if (h === 12) return '12:00 PM';
  return `${String(h-12).padStart(2,'0')}:00 PM`;
}

export function populateHourSelect(sel) {
  sel.innerHTML = '';
  for (let h = 0; h < 24; h++) {
    const opt = document.createElement('option');
    opt.value = h;
    opt.textContent = formatHour(h);
    if (h === new Date().getHours()) opt.selected = true;
    sel.appendChild(opt);
  }
}

export function switchTab(tabId) {
  elements.navTabs.forEach(t => t.classList.remove('active'));
  elements.views.forEach(v => v.classList.remove('active'));
  const targetTab = Array.from(elements.navTabs).find(t => t.dataset.tab === tabId);
  if (targetTab) targetTab.classList.add('active');
  document.getElementById(tabId)?.classList.add('active');
}

export function updateNetworkPulse(allStations) {
  if (!allStations.length) return;

  const currentH = new Date().getHours();
  const isMorningPeak = currentH >= 8 && currentH <= 10;
  const isEveningPeak = currentH >= 17 && currentH <= 20;

  elements.npStationCount.textContent = `${allStations.length} Active Stations`;

  const sorted = [...allStations].sort((a, b) => b.avg_hourly_traffic - a.avg_hourly_traffic);
  if (sorted.length > 0) {
    elements.npTopHub.textContent = sorted[0].name.split(',')[0].replace('Nadaprabhu Kempegowda Station', 'Majestic').trim();
  }

  if (isMorningPeak || isEveningPeak) {
    elements.npTitle.textContent = '⚡ System Rush Hour Active';
    elements.npTitle.style.color = '#d97706';
    elements.npSubtitle.textContent = `High passenger transit load across primary hubs (${isMorningPeak ? 'Morning' : 'Evening'} commute)`;
    elements.npRushHours.textContent = 'Active Peak Window';
  } else {
    elements.npTitle.textContent = '🟢 Network Operating Smoothly';
    elements.npTitle.style.color = '#0f172a';
    elements.npSubtitle.textContent = 'System-wide passenger volume is within optimal capacity';
    elements.npRushHours.textContent = '8:00–10:00 AM · 5:00–8:00 PM';
  }
}

export function renderStationCards(list, sortValue) {
  elements.stationGrid.innerHTML = '';
  if (!list.length) {
    const empty = document.createElement('p');
    empty.className = 'empty-state';
    empty.textContent = 'No stations match your search query.';
    elements.stationGrid.appendChild(empty);
    return;
  }

  list.forEach((s, idx) => {
    const el = document.createElement('div');
    el.className = 'stn-card';

    const header = document.createElement('div');
    header.className = 'stn-header';

    const nameDiv = document.createElement('div');
    nameDiv.className = 'stn-name';
    nameDiv.textContent = s.name;

    const tag = document.createElement('span');
    if (sortValue === 'traffic-desc' && idx < 3) {
      tag.className = 'stn-tag peak-badge';
      tag.textContent = `Top ${idx + 1} Hub`;
    } else {
      tag.className = 'stn-tag';
      tag.textContent = s.traffic_tier.split('/')[0].trim();
    }

    header.appendChild(nameDiv);
    header.appendChild(tag);

    const footer = document.createElement('div');
    footer.className = 'stn-footer';

    const label = document.createElement('span');
    label.className = 'stn-label';
    label.textContent = 'Avg Traffic';

    const avg = document.createElement('span');
    avg.className = 'stn-avg';
    avg.textContent = `${Math.round(s.avg_hourly_traffic)} / hr`;

    footer.appendChild(label);
    footer.appendChild(avg);

    el.appendChild(header);
    el.appendChild(footer);

    el.addEventListener('click', () => openStationModal(s));
    elements.stationGrid.appendChild(el);
  });
}

export function closeModal() {
  elements.modal.classList.add('hidden');
  destroyModalChart();
  currentModalStation = null;
}

export async function openStationModal(station) {
  currentModalStation = station;
  elements.mName.textContent = station.name;
  elements.mTier.textContent = station.traffic_tier;
  elements.mAvg.textContent = `${Math.round(station.avg_hourly_traffic)} / hr`;
  elements.mPeak.textContent = 'Calculating…';
  elements.mDaily.textContent = '…';
  elements.mHeadline.textContent = 'Loading 24-Hour Forecast…';
  elements.mSubtext.textContent = 'Querying live inference model';
  elements.mEmoji.textContent = '⏳';

  elements.modal.classList.remove('hidden');

  try {
    const data = await fetchForecast(station.name, today());

    elements.mPeak.textContent = data.peak_time_label;
    elements.mDaily.textContent = `${data.total_daily_predicted.toLocaleString()} pax`;

    const currentHour = new Date().getHours();
    const currentForecast = data.hourly_forecast.find(p => p.hour === currentHour) || data.hourly_forecast[0];

    if (currentForecast.is_peak_hour) {
      elements.mHeadline.textContent = '⚡ Peak Rush Expected';
      elements.mHeadline.className = 'status-head status-warning';
      elements.mSubtext.textContent = `Peak surge around ${data.peak_time_label} with ~${data.peak_passengers.toLocaleString()} passengers/hr.`;
      elements.mEmoji.textContent = '⚠️';
      elements.mStatusBox.className = 'modal-status-box box-warning';
    } else {
      elements.mHeadline.textContent = 'Expected Normal Flow';
      elements.mHeadline.className = 'status-head status-good';
      elements.mSubtext.textContent = `Current hour traffic is moderate. Peak expected at ${data.peak_time_label}.`;
      elements.mEmoji.textContent = '✅';
      elements.mStatusBox.className = 'modal-status-box box-good';
    }

    renderModalChart(data);
  } catch (err) {
    elements.mHeadline.textContent = 'Station Overview';
    elements.mSubtext.textContent = err.message || 'Historical station profile active';
    elements.mEmoji.textContent = '🚇';
  }
}

export function renderCheckResult(d) {
  const card = document.getElementById('check-result');
  card.classList.remove('hidden');

  const banner = document.getElementById('status-banner');
  const emoji  = document.getElementById('r-emoji');
  const head   = document.getElementById('r-headline');
  const advice = document.getElementById('r-advice');

  const lvl = d.congestion_level;

  if (lvl.includes('NORMAL') || lvl.includes('CLEAR')) {
    banner.className = 'status-banner level-clear';
    emoji.textContent = '✅';
    head.textContent = 'Not Crowded';
    advice.textContent = 'Good time to travel. Expect a smooth journey.';
  } else if (lvl.includes('MODERATE')) {
    banner.className = 'status-banner level-moderate';
    emoji.textContent = '⚠️';
    head.textContent = 'Moderately Busy';
    advice.textContent = 'Some crowd expected. You may need to stand.';
  } else if (lvl.includes('HEAVY')) {
    banner.className = 'status-banner level-heavy';
    emoji.textContent = '🟠';
    head.textContent = 'Very Crowded';
    advice.textContent = 'Heavy rush. Consider waiting 20–30 minutes.';
  } else {
    banner.className = 'status-banner level-critical';
    emoji.textContent = '🔴';
    head.textContent = 'Extremely Crowded';
    advice.textContent = 'Peak surge. Expect long queues and packed trains.';
  }

  document.getElementById('r-pax').textContent = d.predicted_boarding.toLocaleString();
  document.getElementById('r-avg').textContent = `${Math.round(d.station_avg_traffic)} / hr`;
  document.getElementById('r-day').textContent = d.is_weekend ? 'Weekend' : 'Weekday';
  document.getElementById('r-range').textContent =
    `${Math.round(d.confidence_interval.lower_bound)} – ${Math.round(d.confidence_interval.upper_bound)}`;
}

export function renderPlanTable(d) {
  const tbody = document.querySelector('#plan-table tbody');
  tbody.innerHTML = '';
  d.hourly_forecast.forEach(p => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${p.time_label}</strong>${p.is_peak_hour ? ' ⚡' : ''}</td>
      <td class="bold-val">${p.predicted_boarding.toLocaleString()}</td>
      <td class="muted-val">${p.exit_estimate.toLocaleString()}</td>
      <td>
        <span class="crowd-pill ${p.is_peak_hour ? 'pill-warning' : 'pill-normal'}">${p.congestion_level}</span>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

export function renderPlanKPIs(d, allStations) {
  document.getElementById('kpi-total').textContent = d.total_daily_predicted.toLocaleString();
  document.getElementById('kpi-dayname').textContent = `${d.day_name} · ${d.is_weekend ? 'Weekend' : 'Weekday'}`;
  document.getElementById('kpi-peak-time').textContent = d.peak_time_label;
  document.getElementById('kpi-peak-count').textContent = `${d.peak_passengers.toLocaleString()} pax`;
  document.getElementById('kpi-avg').textContent = `${d.average_hourly_passengers.toLocaleString()} / hr`;
  const st = allStations.find(s => s.name === d.station);
  document.getElementById('kpi-tier').textContent = st ? st.traffic_tier.split('/')[0].trim() : '—';
  document.getElementById('kpi-stn-name').textContent = d.station;
}

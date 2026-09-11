let mainChartInstance = null;
let modalChartInstance = null;

const createGradient = (ctx, height) => {
  const grad = ctx.createLinearGradient(0, 0, 0, height);
  grad.addColorStop(0, 'rgba(15, 23, 42, 0.08)');
  grad.addColorStop(1, 'rgba(15, 23, 42, 0)');
  return grad;
};

export function renderMainChart(data) {
  const ctx = document.getElementById('forecastChart').getContext('2d');
  if (mainChartInstance) mainChartInstance.destroy();

  const labels = data.hourly_forecast.map(p => `${p.hour}:00`);
  const vals = data.hourly_forecast.map(p => p.predicted_boarding);
  const colors = data.hourly_forecast.map(p => p.is_peak_hour ? '#d97706' : '#0f172a');
  const radii = data.hourly_forecast.map(p => p.is_peak_hour ? 5 : 3.5);

  mainChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: vals,
        borderColor: '#0f172a',
        backgroundColor: createGradient(ctx, 300),
        borderWidth: 2.2,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: colors,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: radii,
        pointHoverRadius: 6.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 350 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          titleColor: '#ffffff',
          titleFont: { weight: 'bold', size: 13 },
          bodyColor: '#cbd5e1',
          bodyFont: { size: 12 },
          borderColor: '#334155',
          borderWidth: 1,
          padding: 12,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            title: items => data.hourly_forecast[items[0].dataIndex].time_label,
            label: item => {
              const p = data.hourly_forecast[item.dataIndex];
              return [`Boarding: ${p.predicted_boarding.toLocaleString()} pax`, `Crowd Level: ${p.congestion_level}`];
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: '#f1f5f9' },
          ticks: { color: '#64748b', font: { size: 11, family: 'Inter' } }
        },
        y: {
          grid: { color: '#f1f5f9' },
          ticks: { color: '#64748b', font: { size: 11, family: 'Inter' } },
          beginAtZero: true
        }
      }
    }
  });
}

export function renderModalChart(data) {
  const ctx = document.getElementById('modalForecastChart').getContext('2d');
  if (modalChartInstance) modalChartInstance.destroy();

  const labels = data.hourly_forecast.map(p => `${p.hour}:00`);
  const vals = data.hourly_forecast.map(p => p.predicted_boarding);
  const colors = data.hourly_forecast.map(p => p.is_peak_hour ? '#d97706' : '#0f172a');

  modalChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data: vals,
        borderColor: '#0f172a',
        backgroundColor: createGradient(ctx, 180),
        borderWidth: 2,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: colors,
        pointBorderColor: '#ffffff',
        pointBorderWidth: 1.5,
        pointRadius: 3,
        pointHoverRadius: 5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          titleColor: '#ffffff',
          titleFont: { weight: 'bold', size: 12 },
          bodyColor: '#cbd5e1',
          bodyFont: { size: 11 },
          borderColor: '#334155',
          borderWidth: 1,
          padding: 10,
          cornerRadius: 6,
          displayColors: false,
          callbacks: {
            title: items => data.hourly_forecast[items[0].dataIndex].time_label,
            label: item => `Boarding: ${data.hourly_forecast[item.dataIndex].predicted_boarding.toLocaleString()} pax`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#64748b', font: { size: 10, family: 'Inter' }, maxTicksLimit: 8 }
        },
        y: {
          grid: { color: '#f1f5f9' },
          ticks: { color: '#64748b', font: { size: 10, family: 'Inter' } },
          beginAtZero: true
        }
      }
    }
  });
}

export function destroyModalChart() {
  if (modalChartInstance) {
    modalChartInstance.destroy();
    modalChartInstance = null;
  }
}

/**
 * AGROVERSE — Interactive Frontend Controller
 * NASA Space Apps Challenge 2026: Field Shift
 */

(function () {
  'use strict';

  // Navigation State
  let currentSection = 'overview';
  let activeYearFilter = 'all'; // 'all' | '2020'..'2025'
  let rawMonthlyData = [];
  let rawYearlyData = [];
  let rawSeasonalData = [];
  let rawSoilData = [];

  // ====================================================================
  // 1. INITIALIZATION & DATA LOADING
  // ====================================================================
  document.addEventListener('DOMContentLoaded', async () => {
    initNavigation();
    initMobileDrawer();
    initTooltip();

    // Load Initial Data from window or DataService
    await loadInitialDatasets();

    // Render Initial Sections
    renderClimateSection();
    renderSoilSection();
    renderSmapSection();
    renderTrendsSection();
    renderRisksSection();
    initDecisionSupportSection();
    initWhatIfSimulatorSection();
    initClimateHistorySection();

    // Listen to hash changes for deep linking
    window.addEventListener('hashchange', handleHashRouting);
    if (window.location.hash) {
      handleHashRouting();
    }
  });

  async function loadInitialDatasets() {
    try {
      const [mRes, sRes, yRes, seaRes] = await Promise.all([
        DataService.getMonthlyClimate(),
        DataService.getSoilProperties(),
        DataService.getYearlySummary(),
        DataService.getSeasonalSummary(),
      ]);

      rawMonthlyData = mRes.data || [];
      rawSoilData = sRes.properties || [];
      rawYearlyData = yRes.data || [];
      rawSeasonalData = seaRes.data || [];
    } catch (e) {
      console.error('Failed to load initial datasets:', e);
    }
  }

  // ====================================================================
  // 2. NAVIGATION & TAB SWITCHING
  // ====================================================================
  function initNavigation() {
    const navLinks = document.querySelectorAll('.nav a[data-section]');
    navLinks.forEach((link) => {
      link.addEventListener('click', (e) => {
        e.preventDefault();
        const target = link.dataset.section;
        navigateToSection(target);
      });
    });
  }

  function handleHashRouting() {
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(`section-${hash}`)) {
      navigateToSection(hash);
    }
  }

  function navigateToSection(sectionId) {
    currentSection = sectionId;

    // Update active nav link
    document.querySelectorAll('.nav a').forEach((link) => {
      link.classList.toggle('on', link.dataset.section === sectionId);
    });

    // Toggle sections visibility
    const sections = document.querySelectorAll('.dashboard-section');
    sections.forEach((sec) => {
      sec.classList.toggle('active', sec.id === `section-${sectionId}`);
    });

    // Close mobile drawer if open
    closeMobileDrawer();

    // Update URL hash without scroll jump
    if (history.pushState) {
      history.pushState(null, null, `#${sectionId}`);
    }

    // Refresh charts if needed on view switch
    window.dispatchEvent(new Event('resize'));
  }

  function initMobileDrawer() {
    const toggleBtn = document.getElementById('mobileMenuToggle');
    const backdrop = document.getElementById('sidebarBackdrop');
    const side = document.querySelector('.side');

    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        side.classList.toggle('open');
        backdrop.classList.toggle('show');
      });
    }

    if (backdrop) {
      backdrop.addEventListener('click', closeMobileDrawer);
    }
  }

  function closeMobileDrawer() {
    const side = document.querySelector('.side');
    const backdrop = document.getElementById('sidebarBackdrop');
    if (side) side.classList.remove('open');
    if (backdrop) backdrop.classList.remove('show');
  }

  // ====================================================================
  // 3. TOOLTIP ENGINE
  // ====================================================================
  let tooltipEl = null;
  function initTooltip() {
    tooltipEl = document.createElement('div');
    tooltipEl.className = 'chart-tooltip';
    document.body.appendChild(tooltipEl);
  }

  function showTooltip(evt, html) {
    if (!tooltipEl) return;
    tooltipEl.innerHTML = html;
    tooltipEl.style.display = 'block';
    const x = evt.pageX + 12;
    const y = evt.pageY - 28;
    tooltipEl.style.left = `${x}px`;
    tooltipEl.style.top = `${y}px`;
  }

  function hideTooltip() {
    if (tooltipEl) tooltipEl.style.display = 'none';
  }

  // ====================================================================
  // 4. CLIMATE DASHBOARD SECTION
  // ====================================================================
  function getFilteredMonthlyData() {
    if (activeYearFilter === 'all') return rawMonthlyData;
    return rawMonthlyData.filter((r) => String(r.year) === activeYearFilter);
  }

  function renderClimateSection() {
    // Year filter change event
    const yearSelect = document.getElementById('climateYearFilter');
    if (yearSelect && !yearSelect.dataset.bound) {
      yearSelect.dataset.bound = 'true';
      yearSelect.addEventListener('change', (e) => {
        activeYearFilter = e.target.value;
        renderClimateSection();
        renderSmapSection();
      });
    }

    const data = getFilteredMonthlyData();
    if (!data || !data.length) {
      document.getElementById('cKpiRain').textContent = 'No Data';
      document.getElementById('cKpiTemp').textContent = 'No Data';
      document.getElementById('cKpiRh').textContent = 'No Data';
      document.getElementById('cKpiSolar').textContent = 'No Data';
      document.getElementById('cKpiWind').textContent = 'No Data';
      ['climateRainChart', 'climateTempChart', 'climateRhSolarChart'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '<div style="display:grid;place-items:center;height:100%;color:#889;font-weight:600;font-size:13px">No Data Available for selected period</div>';
      });
      return;
    }

    // Compute KPIs
    const totalRain = data.reduce((acc, r) => acc + (r.rainfall_total_mm || 0), 0);
    const avgTemp = data.reduce((acc, r) => acc + (r.temperature_avg_c || 0), 0) / (data.length || 1);
    const avgRh = data.reduce((acc, r) => acc + (r.relative_humidity_pct || 0), 0) / (data.length || 1);
    const avgSolar = data.reduce((acc, r) => acc + (r.solar_radiation_mj_m2_day || 0), 0) / (data.length || 1);
    const avgWind = data.reduce((acc, r) => acc + (r.wind_speed_m_s || 0), 0) / (data.length || 1);

    document.getElementById('cKpiRain').textContent = `${Math.round(totalRain).toLocaleString()} mm`;
    document.getElementById('cKpiTemp').textContent = `${avgTemp.toFixed(1)} °C`;
    document.getElementById('cKpiRh').textContent = `${avgRh.toFixed(1)} %`;
    document.getElementById('cKpiSolar').textContent = `${avgSolar.toFixed(1)} MJ/m²/d`;
    document.getElementById('cKpiWind').textContent = `${avgWind.toFixed(1)} m/s`;

    // Render Charts
    renderMonthlyRainChart(data);
    renderMonthlyTempChart(data);
    renderMonthlyRhSolarChart(data);
  }

  function renderMonthlyRainChart(data) {
    const container = document.getElementById('climateRainChart');
    if (!container) return;

    const maxRain = Math.max(...data.map((d) => d.rainfall_total_mm || 0), 10);
    const w = 700;
    const h = 200;
    const padL = 45;
    const padR = 20;
    const padT = 20;
    const padB = 30;
    const pw = w - padL - padR;
    const ph = h - padT - padB;
    const bw = Math.max(3, pw / data.length - 2);

    let barsSvg = '';
    data.forEach((d, i) => {
      const bh = ((d.rainfall_total_mm || 0) / maxRain) * ph;
      const bx = padL + i * (pw / data.length) + 1;
      const by = padT + (ph - bh);
      barsSvg += `
        <rect class="bar-elem" x="${bx.toFixed(1)}" y="${by.toFixed(1)}" width="${bw.toFixed(1)}" height="${bh.toFixed(1)}" rx="2" fill="#3a86c8"
          data-tt="${d.year_month}: <b>${d.rainfall_total_mm} mm</b>" />
      `;
    });

    // Y Axis ticks
    let yTicks = '';
    for (let k = 0; k <= 3; k++) {
      const v = (maxRain * k) / 3;
      const yPos = padT + ph * (1 - k / 3);
      yTicks += `
        <line x1="${padL}" y1="${yPos.toFixed(1)}" x2="${w - padR}" y2="${yPos.toFixed(1)}" stroke="#e5e9ec" stroke-dasharray="2 2" />
        <text x="${padL - 6}" y="${(yPos + 3).toFixed(1)}" text-anchor="end" font-size="9" fill="#667">${Math.round(v)}</text>
      `;
    }

    // X Axis labels (sample)
    let xLabels = '';
    const step = Math.ceil(data.length / 12);
    data.forEach((d, i) => {
      if (i % step === 0) {
        const xPos = padL + i * (pw / data.length) + bw / 2;
        xLabels += `<text x="${xPos.toFixed(1)}" y="${h - 8}" text-anchor="middle" font-size="8.5" fill="#667">${d.year_month.slice(2)}</text>`;
      }
    });

    container.innerHTML = `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%" preserveAspectRatio="none">
        ${yTicks}
        ${barsSvg}
        ${xLabels}
      </svg>
    `;

    bindChartTooltips(container);
  }

  function renderMonthlyTempChart(data) {
    const container = document.getElementById('climateTempChart');
    if (!container) return;

    const w = 700;
    const h = 200;
    const padL = 40;
    const padR = 20;
    const padT = 20;
    const padB = 30;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    const temps = data.map((d) => d.temperature_avg_c || 25);
    const minT = Math.floor(Math.min(...data.map((d) => d.temperature_min_c || 18)) - 2);
    const maxT = Math.ceil(Math.max(...data.map((d) => d.temperature_max_c || 35)) + 2);

    const getY = (v) => padT + ph * (1 - (v - minT) / (maxT - minT || 1));
    const getX = (i) => padL + i * (pw / (data.length - 1 || 1));

    // Area range between min & max
    let areaPath = `M ${getX(0)} ${getY(data[0].temperature_max_c)}`;
    data.forEach((d, i) => {
      areaPath += ` L ${getX(i).toFixed(1)} ${getY(d.temperature_max_c).toFixed(1)}`;
    });
    for (let i = data.length - 1; i >= 0; i--) {
      areaPath += ` L ${getX(i).toFixed(1)} ${getY(data[i].temperature_min_c).toFixed(1)}`;
    }
    areaPath += ' Z';

    // Mean Temp Line
    let linePath = `M ${getX(0)} ${getY(data[0].temperature_avg_c)}`;
    data.forEach((d, i) => {
      linePath += ` L ${getX(i).toFixed(1)} ${getY(d.temperature_avg_c).toFixed(1)}`;
    });

    // Dots
    let dots = '';
    data.forEach((d, i) => {
      dots += `
        <circle class="dot-elem" cx="${getX(i).toFixed(1)}" cy="${getY(d.temperature_avg_c).toFixed(1)}" r="3" fill="#fff" stroke="#d6453d" stroke-width="2"
          data-tt="${d.year_month}: Avg <b>${d.temperature_avg_c} °C</b><br>(Min mean: ${d.temperature_min_c} °C, Max mean: ${d.temperature_max_c} °C)" />
      `;
    });

    // Y Axis ticks
    let yTicks = '';
    for (let k = 0; k <= 4; k++) {
      const v = minT + ((maxT - minT) * k) / 4;
      const yPos = getY(v);
      yTicks += `
        <line x1="${padL}" y1="${yPos.toFixed(1)}" x2="${w - padR}" y2="${yPos.toFixed(1)}" stroke="#e5e9ec" stroke-dasharray="2 2" />
        <text x="${padL - 6}" y="${(yPos + 3).toFixed(1)}" text-anchor="end" font-size="9" fill="#667">${v.toFixed(0)}°</text>
      `;
    }

    container.innerHTML = `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%" preserveAspectRatio="none">
        ${yTicks}
        <path d="${areaPath}" fill="#d6453d" fill-opacity="0.12" />
        <path d="${linePath}" fill="none" stroke="#d6453d" stroke-width="2.2" />
        ${dots}
      </svg>
    `;

    bindChartTooltips(container);
  }

  function renderMonthlyRhSolarChart(data) {
    const container = document.getElementById('climateRhSolarChart');
    if (!container) return;

    const w = 700;
    const h = 200;
    const padL = 40;
    const padR = 40;
    const padT = 20;
    const padB = 30;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    const getX = (i) => padL + i * (pw / (data.length - 1 || 1));
    const getYRh = (v) => padT + ph * (1 - (v - 30) / (100 - 30));
    const getYSolar = (v) => padT + ph * (1 - (v - 5) / (30 - 5));

    let rhPath = `M ${getX(0)} ${getYRh(data[0].relative_humidity_pct)}`;
    let solarPath = `M ${getX(0)} ${getYSolar(data[0].solar_radiation_mj_m2_day)}`;

    data.forEach((d, i) => {
      rhPath += ` L ${getX(i).toFixed(1)} ${getYRh(d.relative_humidity_pct).toFixed(1)}`;
      solarPath += ` L ${getX(i).toFixed(1)} ${getYSolar(d.solar_radiation_mj_m2_day).toFixed(1)}`;
    });

    let dots = '';
    data.forEach((d, i) => {
      dots += `
        <circle class="dot-elem" cx="${getX(i).toFixed(1)}" cy="${getYRh(d.relative_humidity_pct).toFixed(1)}" r="2.5" fill="#3f9b5b"
          data-tt="${d.year_month}: RH <b>${d.relative_humidity_pct}%</b>" />
        <circle class="dot-elem" cx="${getX(i).toFixed(1)}" cy="${getYSolar(d.solar_radiation_mj_m2_day).toFixed(1)}" r="2.5" fill="#f0a030"
          data-tt="${d.year_month}: Solar <b>${d.solar_radiation_mj_m2_day} MJ/m²/d</b>" />
      `;
    });

    container.innerHTML = `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%" preserveAspectRatio="none">
        <line x1="${padL}" y1="${padT + ph}" x2="${w - padR}" y2="${padT + ph}" stroke="#e5e9ec" />
        <path d="${rhPath}" fill="none" stroke="#3f9b5b" stroke-width="2" />
        <path d="${solarPath}" fill="none" stroke="#f0a030" stroke-width="2" />
        ${dots}
      </svg>
    `;

    bindChartTooltips(container);
  }

  // ====================================================================
  // 5. STATIC SOIL PROPERTIES SECTION
  // ====================================================================
  function renderSoilSection() {
    const grid = document.getElementById('soilPropsGrid');
    if (!grid) return;

    // Strict constraint: only clay, pH, SOC permitted; nitrogen, sand, silt excluded
    const permittedKeys = ['clay_content_pct', 'soil_ph', 'soil_organic_carbon_pct'];
    const safeProps = (rawSoilData || []).filter((p) => permittedKeys.includes(p.key));

    if (!safeProps.length) {
      grid.innerHTML = '<div class="no-data-card" style="padding:16px;color:#889">No verified soil property records available.</div>';
      return;
    }

    grid.innerHTML = safeProps
      .map(
        (p) => `
      <div class="card soil-prop-card">
        <div class="card-head-sm">
          <span class="prop-title">${p.name}</span>
          <span class="prov-badge">${p.status}</span>
        </div>
        <div class="prop-value">${p.value !== null ? p.value : 'No Data'} <span class="prop-unit">${p.unit}</span></div>
        <p class="prop-desc">${p.description}</p>
        <div class="prop-disclaimer">
          <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          Provisional regional estimate · requires core sampling verification
        </div>
      </div>
    `
      )
      .join('');
  }

  // ====================================================================
  // 6. NASA SMAP SOIL MOISTURE SECTION
  // ====================================================================
  function renderSmapSection() {
    const data = getFilteredMonthlyData();
    const container = document.getElementById('smapChart');
    if (!container) return;
    if (!data || !data.length) {
      container.innerHTML = '<div style="display:grid;place-items:center;height:100%;color:#889;font-weight:600;font-size:13px">No Data Available for selected period</div>';
      return;
    }

    // Check for low coverage flags in the active dataset
    const lowCovMonths = data.filter((d) => d.smap_low_coverage_flag === 1);
    const alertBox = document.getElementById('smapLowCoverageAlert');
    if (alertBox) {
      if (lowCovMonths.length > 0) {
        alertBox.style.display = 'flex';
        alertBox.innerHTML = `
          <svg viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <div>
            <b>Low Satellite Observation Coverage Flagged:</b>
            Few valid satellite observations recorded in: ${lowCovMonths.map((m) => m.year_month).join(', ')}. Treat these months as low-confidence.
          </div>
        `;
      } else {
        alertBox.style.display = 'none';
      }
    }

    // Chart Dimensions
    const w = 700;
    const h = 220;
    const padL = 45;
    const padR = 20;
    const padT = 20;
    const padB = 30;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    const minSm = 0.1;
    const maxSm = 0.48;
    const getY = (v) => padT + ph * (1 - (v - minSm) / (maxSm - minSm));
    const getX = (i) => padL + i * (pw / (data.length - 1 || 1));

    let amPath = `M ${getX(0)} ${getY(data[0].smap_am_soil_moisture_m3m3)}`;
    let pmPath = `M ${getX(0)} ${getY(data[0].smap_pm_soil_moisture_m3m3)}`;
    let combPath = `M ${getX(0)} ${getY(data[0].smap_combined_am_pm_m3m3)}`;

    data.forEach((d, i) => {
      amPath += ` L ${getX(i).toFixed(1)} ${getY(d.smap_am_soil_moisture_m3m3).toFixed(1)}`;
      pmPath += ` L ${getX(i).toFixed(1)} ${getY(d.smap_pm_soil_moisture_m3m3).toFixed(1)}`;
      combPath += ` L ${getX(i).toFixed(1)} ${getY(d.smap_combined_am_pm_m3m3).toFixed(1)}`;
    });

    let points = '';
    data.forEach((d, i) => {
      const isLow = d.smap_low_coverage_flag === 1;
      const r = isLow ? 5 : 3;
      const stroke = isLow ? '#d6453d' : '#2f6b45';
      const fill = isLow ? '#fcd9d6' : '#fff';
      points += `
        <circle class="dot-elem" cx="${getX(i).toFixed(1)}" cy="${getY(d.smap_combined_am_pm_m3m3).toFixed(1)}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="2"
          data-tt="${d.year_month} · SMAP Combined: <b>${d.smap_combined_am_pm_m3m3} m³/m³</b><br>AM: ${d.smap_am_soil_moisture_m3m3} (n=${d.smap_am_valid_obs}) · PM: ${d.smap_pm_soil_moisture_m3m3} (n=${d.smap_pm_valid_obs})<br>${isLow ? '<span style=\'color:#d6453d;font-weight:600\'>⚠️ Few valid satellite observations</span>' : 'Standard observation coverage'}" />
      `;
    });

    // Y Axis ticks
    let yTicks = '';
    for (let k = 0; k <= 4; k++) {
      const v = minSm + ((maxSm - minSm) * k) / 4;
      const yPos = getY(v);
      yTicks += `
        <line x1="${padL}" y1="${yPos.toFixed(1)}" x2="${w - padR}" y2="${yPos.toFixed(1)}" stroke="#e5e9ec" stroke-dasharray="2 2" />
        <text x="${padL - 6}" y="${(yPos + 3).toFixed(1)}" text-anchor="end" font-size="9" fill="#667">${v.toFixed(2)}</text>
      `;
    }

    container.innerHTML = `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%" preserveAspectRatio="none">
        ${yTicks}
        <path d="${amPath}" fill="none" stroke="#3a86c8" stroke-width="1.6" stroke-dasharray="4 2" />
        <path d="${pmPath}" fill="none" stroke="#f0a030" stroke-width="1.6" stroke-dasharray="4 2" />
        <path d="${combPath}" fill="none" stroke="#2f6b45" stroke-width="2.6" />
        ${points}
      </svg>
    `;

    bindChartTooltips(container);
  }

  // ====================================================================
  // 7. CLIMATE TRENDS & SEASONAL SECTION
  // ====================================================================
  function renderTrendsSection() {
    renderYearlySummaryChart();
    renderSeasonalCards();
  }

  function renderYearlySummaryChart() {
    const container = document.getElementById('yearlySummaryChart');
    if (!container || !rawYearlyData.length) return;

    const w = 700;
    const h = 210;
    const padL = 45;
    const padR = 20;
    const padT = 20;
    const padB = 30;
    const pw = w - padL - padR;
    const ph = h - padT - padB;

    const maxRain = Math.max(...rawYearlyData.map((y) => y.rainfall_total_mm), 2500);
    const bw = pw / rawYearlyData.length / 2;

    let bars = '';
    rawYearlyData.forEach((d, i) => {
      const bh = (d.rainfall_total_mm / maxRain) * ph;
      const bx = padL + i * (pw / rawYearlyData.length) + bw / 2;
      const by = padT + (ph - bh);
      bars += `
        <rect class="bar-elem" x="${bx.toFixed(1)}" y="${by.toFixed(1)}" width="${bw.toFixed(1)}" height="${bh.toFixed(1)}" rx="3" fill="#3a86c8"
          data-tt="${d.year}: Total Rain <b>${d.rainfall_total_mm} mm</b><br>Rainy days: ${d.rainy_days_count} · Heavy rain days: ${d.heavy_rain_days_count}" />
        <text x="${(bx + bw / 2).toFixed(1)}" y="${h - 8}" text-anchor="middle" font-size="10" font-weight="600" fill="#334">${d.year}</text>
      `;
    });

    let yTicks = '';
    for (let k = 0; k <= 3; k++) {
      const v = (maxRain * k) / 3;
      const yPos = padT + ph * (1 - k / 3);
      yTicks += `
        <line x1="${padL}" y1="${yPos.toFixed(1)}" x2="${w - padR}" y2="${yPos.toFixed(1)}" stroke="#e5e9ec" />
        <text x="${padL - 6}" y="${(yPos + 3).toFixed(1)}" text-anchor="end" font-size="9" fill="#667">${Math.round(v)}</text>
      `;
    }

    container.innerHTML = `
      <svg viewBox="0 0 ${w} ${h}" width="100%" height="100%" preserveAspectRatio="none">
        ${yTicks}
        ${bars}
      </svg>
    `;

    bindChartTooltips(container);
  }

  function renderSeasonalCards() {
    const container = document.getElementById('seasonalGrid');
    if (!container || !rawSeasonalData.length) return;

    // Filter by selected year in trends dropdown or default to 2025
    const seasonYearSelect = document.getElementById('seasonalYearFilter');
    let selYear = 2025;
    if (seasonYearSelect) {
      if (!seasonYearSelect.dataset.bound) {
        seasonYearSelect.dataset.bound = 'true';
        seasonYearSelect.addEventListener('change', () => renderSeasonalCards());
      }
      selYear = Number(seasonYearSelect.value) || 2025;
    }

    const yearSeasons = rawSeasonalData.filter((s) => s.year === selYear);
    container.innerHTML = yearSeasons
      .map(
        (s) => `
      <div class="card season-card">
        <div class="season-badge ${getSeasonClass(s.season)}">${s.season}</div>
        <div class="season-rain">${s.rainfall_total_mm} <small>mm</small></div>
        <div class="season-meta">
          <span>Avg Temp: <b>${s.temperature_avg_c} °C</b></span>
          <span>RH: <b>${s.relative_humidity_pct}%</b></span>
        </div>
        <div class="season-days">
          <div class="day-chip">Rainy days: <b>${s.rainy_days_count}</b></div>
          <div class="day-chip heavy">Heavy rain days: <b>${s.heavy_rain_days_count}</b></div>
        </div>
      </div>
    `
      )
      .join('');
  }

  function getSeasonClass(name) {
    if (name.includes('Monsoon')) return 'monsoon';
    if (name.includes('Summer')) return 'summer';
    if (name.includes('Winter')) return 'winter';
    return 'post-monsoon';
  }

  // ====================================================================
  // 8. RISK INDICATORS SECTION
  // ====================================================================
  function renderRisksSection() {
    const container = document.getElementById('riskCardsContainer');
    if (!container) return;

    // Calculate metrics strictly from real API data; display unavailable when data is absent
    const hasYearlyData = Array.isArray(rawYearlyData) && rawYearlyData.length > 0;
    const nYears = hasYearlyData ? rawYearlyData.length : 0;
    const totalRain = hasYearlyData
      ? rawYearlyData.reduce((acc, y) => acc + (typeof y.rainfall_total_mm === 'number' ? y.rainfall_total_mm : 0), 0)
      : null;
    const avgRain = (hasYearlyData && totalRain !== null && nYears > 0) ? totalRain / nYears : null;
    const baseRain = 1535; // 1991–2020 WMO climatological normal
    const rainDiffPct = (avgRain !== null && baseRain > 0)
      ? ((avgRain - baseRain) / baseRain * 100).toFixed(0)
      : null;

    // Calculate heat days strictly from rawYearlyData
    const hasHeatData = hasYearlyData && rawYearlyData.some(y => typeof y.heat_days_count === 'number');
    const totalHeatDays = hasHeatData
      ? rawYearlyData.reduce((acc, y) => acc + (y.heat_days_count || 0), 0)
      : null;
    const startYr = hasYearlyData ? rawYearlyData[0].year : '';
    const endYr = hasYearlyData ? rawYearlyData[rawYearlyData.length - 1].year : '';
    const yrLabel = (startYr && endYr) ? `(${startYr}–${endYr})` : '';

    const hasMonthlyData = Array.isArray(rawMonthlyData) && rawMonthlyData.length > 0;
    const totalMonths = hasMonthlyData ? rawMonthlyData.length : 0;
    const lowCovMonths = hasMonthlyData
      ? rawMonthlyData.filter(m => m.smap_low_coverage_flag === 1).length
      : 0;
    const validPassPct = (hasMonthlyData && totalMonths > 0)
      ? (((totalMonths - lowCovMonths) / totalMonths) * 100).toFixed(1)
      : null;

    const heatValHtml = totalHeatDays !== null
      ? `${totalHeatDays} <small>Days ≥ 35 °C ${yrLabel}</small>`
      : `<span class="text-muted">No Data Available</span>`;

    const rainValHtml = (totalRain !== null && nYears > 0)
      ? `${Math.round(totalRain).toLocaleString()} <small>mm / ${nYears}-yr cumulative</small>`
      : `<span class="text-muted">No Data Available</span>`;

    const rainDiffChip = rainDiffPct !== null
      ? `<span class="chip-status green">Observational Difference (▲ +${rainDiffPct}% vs Baseline)</span>`
      : `<span class="chip-status unavailable">Unavailable</span>`;

    const smapCoverageVal = validPassPct !== null
      ? `${validPassPct}% <small>Valid Data Retrieval Months</small>`
      : `<span class="text-muted">No Data Available</span>`;

    const smapStatusChip = validPassPct !== null
      ? `<span class="chip-status amber">Regional Satellite Coverage</span>`
      : `<span class="chip-status unavailable">Unavailable</span>`;

    container.innerHTML = `
      <div class="risk-indicator-grid">
        <div class="card risk-ind-card">
          <div class="risk-top">
            <span class="risk-title">Thermal Observational Indicator (≥ 35 °C)</span>
            <span class="chip-status amber">Observational Count</span>
          </div>
          <div class="risk-main-val">${heatValHtml}</div>
          <p class="risk-detail">Empirical count of days reaching 35 °C from NASA POWER daily maximum temperatures. Observational meteorological indicator; not a universal physiological crop stress prediction.</p>
        </div>

        <div class="card risk-ind-card">
          <div class="risk-top">
            <span class="risk-title">Precipitation Historical Comparison</span>
            ${rainDiffChip}
          </div>
          <div class="risk-main-val">${rainValHtml}</div>
          <p class="risk-detail">Compared against the 1991–2020 WMO climatological reference normal (${avgRain !== null ? Math.round(avgRain) : '—'} mm/yr vs 1,535 mm). High precipitation alone does not prove field-level flooding.</p>
        </div>

        <div class="card risk-ind-card">
          <div class="risk-top">
            <span class="risk-title">SMAP Satellite Coverage Status</span>
            ${smapStatusChip}
          </div>
          <div class="risk-main-val">${smapCoverageVal}</div>
          <p class="risk-detail">Approximately 36 km grid observation context (${lowCovMonths} monsoonal cloud/orbit gap months flagged). Regional satellite indicator; not in-situ soil moisture sensor measurements.</p>
        </div>

        <div class="card risk-ind-card">
          <div class="risk-top">
            <span class="risk-title">Groundwater / Deep Aquifer</span>
            <span class="chip-status unavailable">Unavailable</span>
          </div>
          <div class="risk-main-val text-muted">No Data Available</div>
          <p class="risk-detail">Sub-surface hydrological monitoring data requires in-situ piezometer well integration; not estimated from satellite data alone.</p>
        </div>
      </div>
    `;
  }

  // ====================================================================
  // 9. HELPER: BIND TOOLTIPS
  // ====================================================================
  function bindChartTooltips(svgRoot) {
    const targets = svgRoot.querySelectorAll('[data-tt]');
    targets.forEach((elem) => {
      elem.addEventListener('mouseenter', (e) => {
        showTooltip(e, elem.dataset.tt);
      });
      elem.addEventListener('mousemove', (e) => {
        showTooltip(e, elem.dataset.tt);
      });
      elem.addEventListener('mouseleave', hideTooltip);
    });
  }

  // ====================================================================
  // 10. DECISION SUPPORT CONTROLLER (SIX CROPS)
  // ====================================================================
  let currentSuitabilityData = [];

  async function initDecisionSupportSection() {
    const monthSelect = document.getElementById('dsMonthSelect');
    const refreshBtn = document.getElementById('dsRefreshBtn');

    if (refreshBtn && monthSelect) {
      refreshBtn.addEventListener('click', () => {
        loadCropSuitability(parseInt(monthSelect.value, 10));
      });
      monthSelect.addEventListener('change', () => {
        loadCropSuitability(parseInt(monthSelect.value, 10));
      });
    }

    // Initial load for May (default)
    await loadCropSuitability(5);
  }

  async function loadCropSuitability(month) {
    const grid = document.getElementById('cropsCardsGrid');
    const tbody = document.getElementById('cropsTableBody');
    if (!grid || !tbody) return;

    grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--text-muted)">Evaluating observed climate conditions and available crop knowledge...</div>';
    
    const res = await DataService.getCropSuitability(month);
    if (!res || !res.results) {
      grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;color:#d6453d">Failed to load crop evaluations.</div>';
      return;
    }

    currentSuitabilityData = res.results;
    renderCropCards(res.results);
    renderCropComparisonTable(res.results);
  }

  function getStatusBadge(status) {
    if (status === 'Suitable for further consideration') {
      return '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;background:rgba(63,155,91,0.15);color:#2d7a44;border:1px solid #3f9b5b">Suitable for consideration</span>';
    } else if (status === 'Needs careful evaluation') {
      return '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;background:rgba(224,145,44,0.15);color:#b36b00;border:1px solid #e0912c">Needs careful evaluation</span>';
    } else if (status === 'Potentially unsuitable under observed conditions') {
      return '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;background:rgba(214,69,61,0.15);color:#b3241d;border:1px solid #d6453d">Potentially unsuitable</span>';
    }
    return '<span style="display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;background:rgba(120,120,120,0.15);color:#666">Insufficient data</span>';
  }

  function renderCropCards(crops) {
    const grid = document.getElementById('cropsCardsGrid');
    if (!grid) return;

    grid.innerHTML = crops.map(c => {
      const waterVal = c.water_requirement_info ? c.water_requirement_info.crop_water_requirement_value : 'N/A';
      const waterUnit = c.water_requirement_info ? c.water_requirement_info.unit : '';
      const calPatterns = (c.crop_calendar_info || []).map(cal => `${cal.season_or_pattern}: Sowing (${cal.sowing_start}-${cal.sowing_end})`).join('; ') || 'Continuous';
      const supHtml = c.supporting_factors.map(f => `<li style="margin-bottom:3px">✓ ${f}</li>`).join('');
      const riskHtml = c.risk_factors.map(r => `<li style="margin-bottom:3px;color:#b3241d">⚠ ${r}</li>`).join('');
      const score = c.comparative_score !== null ? `${c.comparative_score} / 100` : 'N/A';

      return `
        <div class="card" style="padding:16px;border-radius:10px;display:flex;flex-direction:column;justify-content:space-between">
          <div>
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:8px">
              <div>
                <h3 style="margin:0;font-size:16px;font-weight:700;color:var(--text-main)">${c.crop_name}</h3>
                <span style="font-size:11px;color:var(--text-muted);font-weight:600">Classification: ${c.priority}</span>
              </div>
              <div>${getStatusBadge(c.suitability_status)}</div>
            </div>

            <div style="background:var(--bg-subtle, rgba(0,0,0,0.02));padding:8px;border-radius:6px;font-size:11.5px;margin:8px 0">
              <div><b>Water Requirement:</b> ${waterVal} ${waterUnit} (${c.water_requirement_info.water_requirement_category || 'moderate'})</div>
              <div style="margin-top:3px"><b>Crop Calendar:</b> ${calPatterns}</div>
              <div style="margin-top:3px"><b>Exploratory Index:</b> <b style="color:var(--primary)">${score}</b> <span style="font-size:10.5px;color:var(--text-muted)">(Uncertainty: ${c.uncertainty_level})</span></div>
            </div>

            <div style="margin-top:8px;font-size:11.5px">
              <div style="font-weight:600;color:#2d7a44;margin-bottom:4px">Supporting Climate Factors:</div>
              <ul style="list-style:none;padding-left:0;margin:0 0 8px 0">
                ${supHtml || '<li style="color:var(--text-muted)">None highlighted</li>'}
              </ul>
              <div style="font-weight:600;color:#b3241d;margin-bottom:4px">Empirical Risk Factors:</div>
              <ul style="list-style:none;padding-left:0;margin:0 0 8px 0">
                ${riskHtml || '<li style="color:var(--text-muted)">No acute risks triggered</li>'}
              </ul>
            </div>
          </div>

          <details style="margin-top:10px;font-size:11.5px;background:var(--bg-card);border:1px solid var(--border-color);border-radius:6px;padding:6px 10px">
            <summary style="cursor:pointer;font-weight:600;color:var(--text-main)">View Agronomic Evidence & Verification</summary>
            <div style="margin-top:8px;white-space:pre-line;color:var(--text-muted);line-height:1.5">
              ${c.explanation}
              <div style="margin-top:6px;font-size:10.5px;color:${c.verification_status === 'verified' ? '#2d7a44' : '#b36b00'}"><b>Verification Status:</b> ${c.verification_status || 'Source verification not established'}</div>
            </div>
          </details>
        </div>
      `;
    }).join('');
  }

  function renderCropComparisonTable(crops) {
    const tbody = document.getElementById('cropsTableBody');
    if (!tbody) return;

    tbody.innerHTML = crops.map(c => {
      const waterVal = c.water_requirement_info ? `${c.water_requirement_info.crop_water_requirement_value} ${c.water_requirement_info.unit}` : 'N/A';
      const limitation = c.risk_factors.length ? c.risk_factors[0] : (c.supporting_factors[0] || 'Standard monitoring');
      return `
        <tr style="border-bottom:1px solid var(--border-color)">
          <td style="padding:10px;font-weight:700">${c.crop_name}</td>
          <td><span style="font-size:11px;font-weight:600;color:var(--text-muted)">${c.priority}</span></td>
          <td>${getStatusBadge(c.suitability_status)}</td>
          <td><span style="text-transform:capitalize">${c.water_requirement_info.water_requirement_category || 'moderate'}</span></td>
          <td>${waterVal}</td>
          <td><b>${c.comparative_score}</b> <small>/ 100</small></td>
          <td><span style="font-size:11px">${c.uncertainty_level}</span></td>
          <td style="max-width:240px;color:var(--text-muted)">${limitation}</td>
        </tr>
      `;
    }).join('');
  }

  // ====================================================================
  // 11. WHAT-IF SCENARIO SIMULATOR CONTROLLER
  // ====================================================================
  function initWhatIfSimulatorSection() {
    const rainSlider = document.getElementById('simRainSlider');
    const tempSlider = document.getElementById('simTempSlider');
    const drySlider = document.getElementById('simDrySlider');
    const monthSelect = document.getElementById('simMonthSelect');

    const valRain = document.getElementById('valRainChange');
    const valTemp = document.getElementById('valTempChange');
    const valDry = document.getElementById('valDryChange');

    const btnRun = document.getElementById('btnRunSimulation');
    const btnReset = document.getElementById('btnResetSimulation');

    if (!rainSlider || !btnRun) return;

    rainSlider.addEventListener('input', () => {
      valRain.textContent = `${rainSlider.value > 0 ? '+' : ''}${rainSlider.value}%`;
    });
    tempSlider.addEventListener('input', () => {
      valTemp.textContent = `${tempSlider.value > 0 ? '+' : ''}${parseFloat(tempSlider.value).toFixed(1)} °C`;
    });
    drySlider.addEventListener('input', () => {
      valDry.textContent = `${drySlider.value > 0 ? '+' : ''}${drySlider.value} days`;
    });

    btnReset.addEventListener('click', () => {
      rainSlider.value = 0;
      tempSlider.value = 0;
      drySlider.value = 0;
      valRain.textContent = '0%';
      valTemp.textContent = '+0.0 °C';
      valDry.textContent = '+0 days';
      triggerSimulation();
    });

    btnRun.addEventListener('click', () => {
      triggerSimulation();
    });

    // Run initial baseline vs default scenario
    triggerSimulation();
  }

  async function triggerSimulation() {
    const rainSlider = document.getElementById('simRainSlider');
    const tempSlider = document.getElementById('simTempSlider');
    const drySlider = document.getElementById('simDrySlider');
    const monthSelect = document.getElementById('simMonthSelect');
    const statusMsg = document.getElementById('simStatusMsg');

    if (!rainSlider) return;

    if (statusMsg) statusMsg.textContent = 'Simulating scenario impact...';

    const params = {
      rainfall_pct_change: parseFloat(rainSlider.value),
      temperature_delta_c: parseFloat(tempSlider.value),
      dry_spell_delta_days: parseInt(drySlider.value, 10),
      target_month: parseInt(monthSelect.value, 10)
    };

    const res = await DataService.runScenarioSimulation(params);
    if (!res || !res.simulation) {
      if (statusMsg) statusMsg.textContent = 'Simulation failed. Check parameters.';
      return;
    }

    if (statusMsg) statusMsg.textContent = 'Simulation complete.';
    renderSimulationOutputs(res.simulation);
  }

  function renderSimulationOutputs(sim) {
    const bar = document.getElementById('simConditionsBar');
    const tbody = document.getElementById('simResultsTableBody');
    if (!bar || !tbody) return;

    const b = sim.baseline_conditions;
    const s = sim.scenario_conditions;

    bar.innerHTML = `
      <div style="padding:10px;background:var(--bg-subtle, rgba(0,0,0,0.02));border-radius:8px;border:1px solid var(--border-color)">
        <span style="font-size:11px;font-weight:600;color:var(--text-muted);display:block">Rainfall (Monthly)</span>
        <b style="font-size:14px;color:var(--text-main)">${s.rainfall_mm} mm</b>
        <div style="font-size:11px;color:var(--text-muted)">Baseline: ${b.rainfall_mm} mm (${sim.parameters.rainfall_pct_change > 0 ? '+' : ''}${sim.parameters.rainfall_pct_change}%)</div>
      </div>
      <div style="padding:10px;background:var(--bg-subtle, rgba(0,0,0,0.02));border-radius:8px;border:1px solid var(--border-color)">
        <span style="font-size:11px;font-weight:600;color:var(--text-muted);display:block">Average Temperature</span>
        <b style="font-size:14px;color:var(--text-main)">${s.average_temperature_c} °C</b>
        <div style="font-size:11px;color:var(--text-muted)">Baseline: ${b.average_temperature_c} °C (${sim.parameters.temperature_delta_c > 0 ? '+' : ''}${sim.parameters.temperature_delta_c} °C)</div>
      </div>
      <div style="padding:10px;background:var(--bg-subtle, rgba(0,0,0,0.02));border-radius:8px;border:1px solid var(--border-color)">
        <span style="font-size:11px;font-weight:600;color:var(--text-muted);display:block">Longest Dry Spell</span>
        <b style="font-size:14px;color:var(--text-main)">${s.longest_dry_spell_days} days</b>
        <div style="font-size:11px;color:var(--text-muted)">Baseline: ${b.longest_dry_spell_days} days (${sim.parameters.dry_spell_delta_days > 0 ? '+' : ''}${sim.parameters.dry_spell_delta_days} d)</div>
      </div>
      <div style="padding:10px;background:var(--bg-subtle, rgba(0,0,0,0.02));border-radius:8px;border:1px solid var(--border-color)">
        <span style="font-size:11px;font-weight:600;color:var(--text-muted);display:block">Satellite Soil Moisture</span>
        <b style="font-size:14px;color:var(--text-main)">${b.soil_moisture_am ? b.soil_moisture_am.toFixed(3) : 'N/A'} <small>cm³/cm³</small></b>
        <div style="font-size:10.5px;color:#2d7a44">Unaltered / Not Fabricated</div>
      </div>
    `;

    tbody.innerHTML = sim.crop_comparisons.map(c => {
      const shiftTag = c.status_changed 
        ? '<span style="color:#b3241d;font-weight:700">Shifted Alert</span>' 
        : '<span style="color:#2d7a44;font-weight:600">Stable</span>';
      
      const scoreDeltaTag = c.score_delta > 0 
        ? `<b style="color:#2d7a44">+${c.score_delta}</b>` 
        : (c.score_delta < 0 ? `<b style="color:#b3241d">${c.score_delta}</b>` : '<span>0.0</span>');

      const newRisksHtml = c.new_risks.length 
        ? c.new_risks.map(r => `<div style="color:#b3241d">+ ${r}</div>`).join('') 
        : '<span style="color:var(--text-muted)">None</span>';

      const mitRisksHtml = c.reduced_risks.length 
        ? c.reduced_risks.map(r => `<div style="color:#2d7a44">- ${r}</div>`).join('') 
        : '<span style="color:var(--text-muted)">None</span>';

      return `
        <tr style="border-bottom:1px solid var(--border-color)">
          <td style="padding:10px;font-weight:700">${c.crop_name}</td>
          <td>${getStatusBadge(c.baseline_status)}</td>
          <td>${getStatusBadge(c.scenario_status)}</td>
          <td>${shiftTag}</td>
          <td>${c.baseline_score} -> <b>${c.scenario_score}</b> (${scoreDeltaTag})</td>
          <td style="font-size:11px">${newRisksHtml}</td>
          <td style="font-size:11px">${mitRisksHtml}</td>
          <td style="max-width:240px;font-size:11.5px;color:var(--text-muted)">
            ${c.reasons_for_change.join(' ')}
          </td>
        </tr>
      `;
    }).join('');
  }

  // ====================================================================
  // 12. HISTORICAL CLIMATE INTELLIGENCE CONTROLLER (MEMBER 3)
  // ====================================================================
  async function initClimateHistorySection() {
    const topRainEl = document.getElementById('topRainfallList');
    const dryPeriodsEl = document.getElementById('dryPeriodsList');
    const riskTbody = document.getElementById('riskAssessmentTableBody');

    if (!topRainEl || !riskTbody) return;

    try {
      const [histRes, riskRes] = await Promise.all([
        DataService.getClimateHistory(),
        DataService.getRiskAssessment()
      ]);

      if (histRes && histRes.climate_history) {
        const h = histRes.climate_history;
        if (h.top_rainfall_days && topRainEl) {
          topRainEl.innerHTML = h.top_rainfall_days.slice(0, 5).map(r => `
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border-color);padding:4px 0">
              <span><b>${r.date}</b></span>
              <b style="color:#3a86c8">${parseFloat(r.PRECTOTCORR).toFixed(1)} mm</b>
            </div>
          `).join('');
        }

        if (h.dry_periods && dryPeriodsEl) {
          dryPeriodsEl.innerHTML = h.dry_periods.slice(0, 5).map(d => `
            <div style="display:flex;justify-content:space-between;border-bottom:1px solid var(--border-color);padding:4px 0">
              <span>${d.start_date} to ${d.end_date}</span>
              <b style="color:#e0912c">${d.duration_days} days</b>
            </div>
          `).join('');
        }
      }

      if (riskRes && riskRes.risk_assessment && riskRes.risk_assessment.data) {
        const rows = riskRes.risk_assessment.data;
        riskTbody.innerHTML = rows.map(r => `
          <tr style="border-bottom:1px solid var(--border-color)">
            <td style="padding:6px 8px;font-weight:600">${r.year}-${String(r.month).padStart(2, '0')}</td>
            <td>${parseFloat(r.rainfall_mm).toFixed(1)}</td>
            <td>${parseFloat(r.average_temperature_c).toFixed(1)}</td>
            <td>${r.longest_dry_spell_days}</td>
            <td>${r.dry_spell_7plus_days === 'True' ? '<span style="color:#b3241d;font-weight:700">Yes (7+ d)</span>' : '<span style="color:#2d7a44">No</span>'}</td>
            <td>${r.heavy_rain_month_indicator === 'True' ? '<span style="color:#3a86c8;font-weight:700">Heavy</span>' : '<span style="color:var(--text-muted)">Normal</span>'}</td>
            <td>${r.AM_mean ? parseFloat(r.AM_mean).toFixed(3) : '<span style="color:var(--text-muted)">null</span>'}</td>
            <td>${r.AM_low_soil_moisture_relative === 'True' ? '<span style="color:#e0912c;font-weight:600">Low</span>' : '<span>Normal</span>'}</td>
          </tr>
        `).join('');
      }
    } catch (e) {
      console.error('Failed to load historical climate intelligence:', e);
    }
  }

})();

/**
 * AGROVERSE — Client Data Service Layer
 * NASA Space Apps Challenge 2026: Field Shift
 *
 * Encapsulates all API communication and data contracts, ensuring
 * scientific labeling, missing-value preservation (null is never 0),
 * and seamless fallback between live API responses and initial JSON payloads.
 *
 * Integrated with Decision Support and What-If Scenario APIs.
 */

const DataService = {
  // In-memory cache
  _cache: {},

  /**
   * Fetch Monthly Climate & SMAP Data (2020-01 to 2025-12)
   */
  async getMonthlyClimate(fromYM = null, toYM = null) {
    let url = '/api/monthly';
    const params = new URLSearchParams();
    if (fromYM) params.append('from', fromYM);
    if (toYM) params.append('to', toYM);
    if (params.toString()) url += `?${params.toString()}`;

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return { success: true, meta: json.meta || {}, data: json.data || [] };
    } catch (err) {
      console.warn('API call failed, attempting initial window payload:', err);
      if (window.INITIAL_DATA && window.INITIAL_DATA.monthly) {
        let rows = window.INITIAL_DATA.monthly.data || [];
        if (fromYM) rows = rows.filter(r => r.year_month >= fromYM);
        if (toYM) rows = rows.filter(r => r.year_month <= toYM);
        return { success: true, meta: window.INITIAL_DATA.monthly.meta, data: rows };
      }
      return { success: false, error: err.message, data: [] };
    }
  },

  /**
   * Fetch Static Soil Properties (Provisional)
   */
  async getSoilProperties() {
    try {
      const res = await fetch('/api/soil');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return { success: true, meta: json.meta || {}, properties: json.properties || [] };
    } catch (err) {
      if (window.INITIAL_DATA && window.INITIAL_DATA.soil) {
        return { success: true, ...window.INITIAL_DATA.soil };
      }
      return { success: false, error: err.message, properties: [] };
    }
  },

  /**
   * Fetch Yearly Climate Summary (2020-2025)
   */
  async getYearlySummary() {
    try {
      const res = await fetch('/api/yearly');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return { success: true, meta: json.meta || {}, data: json.data || [] };
    } catch (err) {
      if (window.INITIAL_DATA && window.INITIAL_DATA.yearly) {
        return { success: true, ...window.INITIAL_DATA.yearly };
      }
      return { success: false, error: err.message, data: [] };
    }
  },

  /**
   * Fetch Seasonal Climate Summary (24 records)
   */
  async getSeasonalSummary() {
    try {
      const res = await fetch('/api/seasonal');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return { success: true, meta: json.meta || {}, data: json.data || [] };
    } catch (err) {
      if (window.INITIAL_DATA && window.INITIAL_DATA.seasonal) {
        return { success: true, ...window.INITIAL_DATA.seasonal };
      }
      return { success: false, error: err.message, data: [] };
    }
  },

  /**
   * Fetch Daily Cleaned SMAP Soil Moisture (2,192 records, 2020-01-01 to 2025-12-31)
   */
  async getDailySmap(fromDate = null, toDate = null) {
    let url = '/api/smap-daily';
    const params = new URLSearchParams();
    if (fromDate) params.append('from', fromDate);
    if (toDate) params.append('to', toDate);
    if (params.toString()) url += `?${params.toString()}`;

    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return { success: true, meta: json.meta || {}, data: json.data || [] };
    } catch (err) {
      return { success: false, error: err.message, data: [] };
    }
  },

  // ==================================================================
  // DECISION SUPPORT & WHAT-IF SCENARIO API INTEGRATION
  // ==================================================================

  /**
   * Fetch Decision Support Overview (Spatial locations, Source Registry, Crops)
   */
  async getDecisionSupportOverview() {
    try {
      const res = await fetch('/api/decision-support/overview');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to get decision support overview:', err);
      return { status: 'error', error: err.message };
    }
  },

  /**
   * Fetch Crop Suitability Evaluations for a selected month (1-12)
   */
  async getCropSuitability(month = 5) {
    try {
      const res = await fetch(`/api/decision-support/suitability?month=${month}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error(`Failed to get crop suitability for month ${month}:`, err);
      return { status: 'error', error: err.message, results: [] };
    }
  },

  /**
   * Fetch Single Crop Suitability
   */
  async getSingleCropSuitability(cropId, month = 5) {
    try {
      const res = await fetch(`/api/decision-support/suitability/${cropId}?month=${month}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { status: 'error', error: err.message };
    }
  },

  /**
   * Fetch Member 3 Integrated Climate History
   */
  async getClimateHistory() {
    try {
      const res = await fetch('/api/decision-support/climate-history');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { status: 'error', error: err.message };
    }
  },

  /**
   * Fetch Member 3 Risk Assessment Table
   */
  async getRiskAssessment() {
    try {
      const res = await fetch('/api/decision-support/risk-assessment');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { status: 'error', error: err.message };
    }
  },

  /**
   * Fetch Data Quality & Automated Validation Report
   */
  async getDataQualityReport() {
    try {
      const res = await fetch('/api/decision-support/data-quality');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      return { status: 'error', error: err.message };
    }
  },

  /**
   * Run What-if Climate Scenario Simulation (POST)
   */
  async runScenarioSimulation(params) {
    try {
      const res = await fetch('/api/decision-support/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.error('Failed to run scenario simulation:', err);
      return { status: 'error', error: err.message };
    }
  }
};

window.DataService = DataService;

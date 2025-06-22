import { ScatterManager } from "../components/scatter-manager.js";
import { ChartManager } from "../components/chart-manager.js";
import { ModalManager } from "../components/modal-manager.js";
import { Utils } from "../core/utils.js";

/**
 * Analysis Detail Page Controller
 */
class AnalysisDetailPage {
  constructor() {
    this.analysisId = window.ANALYSIS_ID; // Set from template
    this.scatterManager = new ScatterManager(this.analysisId);
    this.chartManager = new ChartManager();
    this.addScatterModal = new ModalManager("addScatterModal");

    // Make chart manager globally available
    window.chartManager = this.chartManager;

    this.initializeEventListeners();
    this.initializePage();
  }

  initializeEventListeners() {
    // Add scatter button
    document
      .getElementById("add-scatter-btn")
      ?.addEventListener("click", () => {
        this.addScatterModal.show();
      });

    // Save scatter button
    document
      .getElementById("save-scatter-btn")
      ?.addEventListener("click", () => {
        this.handleAddScatter();
      });
  }

  async handleAddScatter() {
    const country = document.getElementById("scatter-country").value;
    const date = document.getElementById("scatter-date").value;

    if (!country || !date) {
      Utils.showAlert("Please select both country and date");
      return;
    }

    const saveBtn = document.getElementById("save-scatter-btn");
    Utils.setButtonLoading(saveBtn, true, "Adding...");

    try {
      await this.scatterManager.addNewScatter(country, date);
      this.addScatterModal.hide();
    } catch (error) {
      // Error handled in scatter manager
    } finally {
      Utils.setButtonLoading(saveBtn, false);
    }
  }

  async initializePage() {
    // Initialize chart
    this.chartManager.initializeEmptyChart();

    // Set up date input with restrictions based on available data
    await this.setupDateInput();

    // Auto-load chart if there are scatters
    if (window.HAS_SCATTERS) {
      this.chartManager.loadAllSelectedScatters();
    }
  }

  async setupDateInput() {
    const dateInput = document.getElementById("scatter-date");
    if (!dateInput) return;

    try {
      // Fetch the available date range from the API
      const response = await fetch("/yield-curves/api/bond-date-range/", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": Utils.getCsrfToken(),
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const dateRange = await response.json();

      // Set the date input constraints
      dateInput.min = dateRange.min_date;
      dateInput.max = dateRange.max_date;
      dateInput.value = dateRange.default_date;

      console.log(
        `Date range configured: ${dateRange.min_date} to ${dateRange.max_date}, default: ${dateRange.default_date}`,
      );
    } catch (error) {
      console.error("Failed to fetch bond date range:", error);
      // Fallback: set default to today if API call fails
      dateInput.valueAsDate = new Date();
      Utils.showAlert(
        "Warning: Could not load available date range. Please ensure you select a date with available bond data.",
      );
    }
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  new AnalysisDetailPage();
});

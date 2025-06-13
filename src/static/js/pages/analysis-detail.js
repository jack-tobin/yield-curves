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

  initializePage() {
    // Set default date to today
    const dateInput = document.getElementById("scatter-date");
    if (dateInput) {
      dateInput.valueAsDate = new Date();
    }

    // Initialize chart
    this.chartManager.initializeEmptyChart();

    // Auto-load chart if there are scatters
    if (window.HAS_SCATTERS) {
      this.chartManager.loadAllSelectedScatters();
    }
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  new AnalysisDetailPage();
});

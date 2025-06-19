import { API } from "../core/api.js";
import { Utils } from "../core/utils.js";

/**
 * Scatter management functionality
 */
export class ScatterManager {
  constructor(analysisId) {
    this.analysisId = analysisId;
    this.initializeEventListeners();
  }

  initializeEventListeners() {
    // Scatter chip click to toggle visibility
    document.addEventListener("click", (e) => {
      if (
        e.target.closest(".scatter-chip") &&
        !e.target.classList.contains("delete-scatter-btn") &&
        !e.target.classList.contains("toggle-zero-curve-btn") &&
        !e.target.closest(".scatter-menu-btn") &&
        !e.target.closest(".dropdown")
      ) {
        this.toggleScatterVisibility(e);
      }

      // Delete scatter button
      if (e.target.classList.contains("delete-scatter-btn")) {
        e.preventDefault();
        e.stopPropagation();
        const scatterId = e.target.dataset.scatterId;
        this.deleteScatter(scatterId);
      }

      // Toggle zero curve button
      if (
        e.target.classList.contains("toggle-zero-curve-btn") ||
        e.target.closest(".toggle-zero-curve-btn")
      ) {
        e.preventDefault();
        e.stopPropagation();
        const btn = e.target.classList.contains("toggle-zero-curve-btn")
          ? e.target
          : e.target.closest(".toggle-zero-curve-btn");
        const scatterId = btn.dataset.scatterId;
        this.toggleZeroCurve(scatterId);
      }
    });
  }

  toggleScatterVisibility(e) {
    e.preventDefault();
    const chip = e.target.closest(".scatter-chip");
    const isVisible = chip.dataset.visible === "true";
    chip.dataset.visible = !isVisible;
    // Trigger chart update
    window.chartManager?.loadAllSelectedScatters();
  }

  async deleteScatter(scatterId) {
    try {
      await API.delete(
        `/yield-curves/analysis/${this.analysisId}/scatter/${scatterId}/delete/`,
      );

      // Remove the chip from DOM
      const chip = document.querySelector(`[data-scatter-id="${scatterId}"]`);
      if (chip) {
        chip.remove();
      }

      // Reload chart
      window.chartManager?.loadAllSelectedScatters();

      // No need to show empty state - Add button always remains
    } catch (error) {
      Utils.showAlert("Error deleting scatter. Please try again.");
    }
  }

  async toggleZeroCurve(scatterId) {
    const chip = document.querySelector(`[data-scatter-id="${scatterId}"]`);
    const isZeroCurveEnabled = chip.dataset.zeroCurve === "true";
    const toggleBtn = chip.querySelector(".toggle-zero-curve-btn");
    const zeroCurveText = toggleBtn.querySelector(".zero-curve-text");
    const icon = toggleBtn.querySelector("i");

    try {
      if (!isZeroCurveEnabled) {
        // Enable zero curve
        chip.dataset.zeroCurve = "true";
        zeroCurveText.textContent = "Hide Zero Curve";
        icon.className = "fas fa-chart-line me-2";

        // Load zero curve data
        await window.chartManager?.loadZeroCurveData(scatterId);
      } else {
        // Disable zero curve
        chip.dataset.zeroCurve = "false";
        zeroCurveText.textContent = "Show Zero Curve";
        icon.className = "fas fa-chart-line me-2";

        // Remove zero curve from chart
        window.chartManager?.removeZeroCurveData(scatterId);
      }

      // Refresh chart
      window.chartManager?.loadAllSelectedScatters();
    } catch (error) {
      console.error("Error building zero curve:", error);
      Utils.showAlert("Error building zero curve. Please try again.");

      // Reset state on error
      chip.dataset.zeroCurve = isZeroCurveEnabled ? "true" : "false";
      zeroCurveText.textContent = isZeroCurveEnabled
        ? "Hide Zero Curve"
        : "Show Zero Curve";
    }
  }

  async addNewScatter(country, date) {
    try {
      const data = await API.post(
        `/yield-curves/analysis/${this.analysisId}/scatter/add`,
        {
          country,
          date,
        },
      );

      if (data.success) {
        window.location.reload();
      } else {
        Utils.showAlert("Error: " + data.error);
      }
    } catch (error) {
      Utils.showAlert("Error adding scatter. Please try again.");
    }
  }
}

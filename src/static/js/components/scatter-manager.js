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
        !e.target.classList.contains("delete-scatter-btn")
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

  async addNewScatter(country, date) {
    try {
      const data = await API.post(
        `/yield-curves/analysis/${this.analysisId}/add_scatter/`,
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

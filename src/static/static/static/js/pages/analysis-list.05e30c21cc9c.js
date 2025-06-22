import { API } from "../core/api.js";
import { Utils } from "../core/utils.js";
import { ModalManager } from "../components/modal-manager.js";

/**
 * Analyses List Page Controller
 */
class AnalysesListPage {
  constructor() {
    this.addAnalysisModal = new ModalManager("addAnalysisModal");
    this.initializeEventListeners();
  }

  initializeEventListeners() {
    // Add analysis button
    document
      .getElementById("add-analysis-btn")
      ?.addEventListener("click", () => {
        this.addAnalysisModal.show();
      });

    // Save analysis button
    document
      .getElementById("save-analysis-btn")
      ?.addEventListener("click", () => {
        this.handleAddAnalysis();
      });
  }

  async handleAddAnalysis() {
    const name = document.getElementById("analysis-name").value.trim();

    if (!name) {
      Utils.showAlert("Please enter an analysis name");
      return;
    }

    const saveBtn = document.getElementById("save-analysis-btn");
    Utils.setButtonLoading(saveBtn, true, "Creating...");

    try {
      // Get the create analysis URL from the template
      const createUrl =
        document.querySelector("[data-create-url]")?.dataset.createUrl;
      if (!createUrl) {
        throw new Error("Create URL not found");
      }

      const data = await API.post(createUrl, { name });

      if (data.success) {
        // Close modal
        this.addAnalysisModal.hide();
        // Navigate to the new analysis
        window.location.href = data.redirect_url;
      } else {
        Utils.showAlert("Error: " + data.error);
      }
    } catch (error) {
      console.error("Error creating analysis:", error);
      Utils.showAlert("Error creating analysis: " + error.message);
    } finally {
      Utils.setButtonLoading(saveBtn, false);
    }
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  new AnalysesListPage();
});

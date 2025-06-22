/**
 * Common utility functions
 */
export const Utils = {
  getCsrfToken() {
    const tokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!tokenInput) {
      console.error("CSRF token not found");
      return "";
    }
    return tokenInput.value;
  },

  showAlert(message, type = "error") {
    alert(message); // Can be replaced with a better notification system
  },

  setButtonLoading(button, isLoading, loadingText = "Loading...") {
    if (isLoading) {
      button.dataset.originalText = button.textContent;
      button.textContent = loadingText;
      button.disabled = true;
      button.classList.add("btn-loading");
    } else {
      button.textContent = button.dataset.originalText;
      button.disabled = false;
      button.classList.remove("btn-loading");
    }
  },
};

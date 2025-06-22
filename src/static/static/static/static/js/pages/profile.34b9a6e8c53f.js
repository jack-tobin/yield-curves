/**
 * Profile Page Controller
 */
class ProfilePage {
  constructor() {
    this.initializePage();
  }

  initializePage() {
    // Clear password fields if profile update is successful
    const alerts = document.querySelectorAll(".alert-success");
    if (alerts.length > 0) {
      // Clear password fields
      const currentPassword = document.getElementById("current_password");
      const newPassword = document.getElementById("new_password");
      const confirmPassword = document.getElementById("confirm_password");

      if (currentPassword) currentPassword.value = "";
      if (newPassword) newPassword.value = "";
      if (confirmPassword) confirmPassword.value = "";
    }
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  new ProfilePage();
});

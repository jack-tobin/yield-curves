/**
 * Modal management functionality
 */
export class ModalManager {
  constructor(modalId) {
    this.modalId = modalId;
    this.modal = null;
  }

  show() {
    if (!this.modal) {
      this.modal = new bootstrap.Modal(document.getElementById(this.modalId));
    }
    this.modal.show();
  }

  hide() {
    if (this.modal) {
      this.modal.hide();
    }
  }

  static getInstance(modalId) {
    return bootstrap.Modal.getInstance(document.getElementById(modalId));
  }
}

// Login Page JavaScript - Smooth interactions and form handling
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('.input-field');

    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });

    // Form validation feedback
    const form = document.querySelector('form');
    form.addEventListener('submit', function(e) {
        const button = form.querySelector('button[type="submit"]');
        button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Signing in...';
        button.disabled = true;
    });
});
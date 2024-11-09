// static/js/accounts.js
// static/js/accounts.js

// Toggle password visibility
document.getElementById('showPasswordSignup')?.addEventListener('change', function() {
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        field.type = this.checked ? 'text' : 'password';
    });
});

// Real-time form validation and password strength meter (optional)
(() => {
    'use strict';
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach((form) => {
        form.addEventListener('submit', (event) => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
})();


document.getElementById('showPasswordLogin')?.addEventListener('change', function() {
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(field => {
        field.type = this.checked ? 'text' : 'password';
    });
});

// Password strength validation
const passwordInput = document.getElementById('password1');
const strengthMeter = document.getElementById('passwordStrengthMeter');
const strengthText = document.getElementById('passwordStrengthText');

passwordInput?.addEventListener('input', function() {
    const strength = checkPasswordStrength(passwordInput.value);
    updateStrengthMeter(strength);
});

function checkPasswordStrength(password) {
    let strengthScore = 0;
    if (password.length >= 8) strengthScore += 1;
    if (/[A-Z]/.test(password)) strengthScore += 1;
    if (/[a-z]/.test(password)) strengthScore += 1;
    if (/[0-9]/.test(password)) strengthScore += 1;
    if (/[^A-Za-z0-9]/.test(password)) strengthScore += 1;
    return strengthScore;
}

function updateStrengthMeter(strength) {
    strengthMeter.className = 'progress-bar';
    strengthMeter.style.width = (strength * 20) + '%';
    const strengthLevels = ['Too weak', 'Weak', 'Medium', 'Strong'];
    const colors = ['bg-danger', 'bg-warning', 'bg-info', 'bg-success'];
    strengthText.innerText = strengthLevels[strength] || 'Too weak';
    strengthMeter.classList.add(colors[strength] || 'bg-danger');
}

document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('toggle-password');
    const togglePasswordRepeat = document.getElementById('toggle-password-repeat');
    const passwordInput = document.getElementById('password');
    const repeatPasswordInput = document.getElementById('repeat-password');

    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        this.textContent = type === 'password' ? 'Показать' : 'Скрыть';
    });

    togglePasswordRepeat.addEventListener('click', function() {
        const type = repeatPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        repeatPasswordInput.setAttribute('type', type);
        this.textContent = type === 'password' ? 'Показать' : 'Скрыть';
    });
});
document.addEventListener('DOMContentLoaded', function() {
    function closeAlert(alert) {
        alert.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        alert.style.display = 'flex';
        
        const timeout = parseInt(alert.getAttribute('data-timeout')) || 5000;
        const timer = setTimeout(() => {
            closeAlert(alert);
        }, timeout);
        const closeBtn = alert.querySelector('.close-button');
        closeBtn.addEventListener('click', function() {
            clearTimeout(timer);
            closeAlert(alert);
        });
    });
});
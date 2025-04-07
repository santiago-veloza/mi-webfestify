// Espera 3 segundos y luego desvanece los mensajes flash
setTimeout(function () {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (flash) {
        flash.style.transition = 'opacity 1.5s ease';
        flash.style.opacity = '0';
        setTimeout(() => flash.remove(), 500); // Elimina tras desvanecerse
    });
}, 2000);

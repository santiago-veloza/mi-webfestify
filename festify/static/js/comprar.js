document.addEventListener('DOMContentLoaded', () => {
    const inputCantidad = document.getElementById('cantidad');
    const totalSpan = document.getElementById('total');

    inputCantidad.addEventListener('input', () => {
        const cantidad = parseInt(inputCantidad.value) || 0;
        const total = cantidad * precioBoleta;

        totalSpan.textContent = `$${total.toLocaleString('es-CO')}`;
    });
});
console.log("Script de comprar.js cargado");

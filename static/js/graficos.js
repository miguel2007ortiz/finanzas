// Esperamos a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", function() {
    // Capturamos las etiquetas y datos inyectados en las variables globales del HTML
    const labels = window.datosGraficoLabels || [];
    const data = window.datosGraficoValores || [];

    // Si no hay datos, no dibujamos nada para evitar errores visuales
    if (data.length === 0) return;

    const ctx = document.getElementById('chartGastos').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#4f46e5', // Indigo
                    '#f43f5e', // Rose
                    '#06b6d4', // Cyan
                    '#eab308', // Yellow
                    '#10b981', // Emerald
                    '#8b5cf6'  // Violet
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        font: { size: 12, family: 'sans-serif' },
                        color: '#475569'
                    }
                }
            }
        }
    });
});

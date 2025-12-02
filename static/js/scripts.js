// Scripts globales para el dashboard

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    inicializarTooltips();
    inicializarEventListeners();
    configurarAutoRefresh();
    animarElementos();
});

// Inicializar tooltips de Bootstrap
function inicializarTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Configurar escuchadores de eventos
function inicializarEventListeners() {
    // Exportar datos
    const exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const format = this.dataset.format;
            exportarDatos(format);
        });
    });
    
    // Descargar gráficos
    const downloadButtons = document.querySelectorAll('.download-chart');
    downloadButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const chartId = this.dataset.chartId;
            const format = this.dataset.format || 'png';
            descargarGrafico(chartId, format);
        });
    });
}

// Configurar actualización automática
function configurarAutoRefresh() {
    // Actualizar cada 60 segundos si estamos en dashboard
    if (window.location.pathname.includes('/dashboard')) {
        setInterval(actualizarKPIs, 60000);
    }
}

// Actualizar KPIs desde API
function actualizarKPIs() {
    fetch('/api/kpis')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta de la API');
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error en KPIs:', data.error);
                return;
            }
            
            // Actualizar elementos con datos
            actualizarElementosKPIs(data);
            
            // Mostrar notificación de actualización
            mostrarNotificacion('KPIs actualizados', 'success');
        })
        .catch(error => {
            console.error('Error actualizando KPIs:', error);
            mostrarNotificacion('Error actualizando datos', 'error');
        });
}

// Actualizar elementos del DOM con nuevos KPIs
function actualizarElementosKPIs(data) {
    // Buscar y actualizar elementos con clase kpi-value
    document.querySelectorAll('.kpi-value').forEach(element => {
        const kpiName = element.parentElement.querySelector('.kpi-title')?.textContent;
        if (!kpiName) return;
        
        if (kpiName.includes('Total')) {
            element.textContent = data.total_iguanas;
        } else if (kpiName.includes('Peso Promedio')) {
            element.textContent = data.peso_promedio + ' kg';
        } else if (kpiName.includes('Proporción Machos')) {
            element.textContent = data.proporcion_machos + '%';
        } else if (kpiName.includes('Adultos Dominantes')) {
            element.textContent = data.total_adultos;
        }
    });
}

// Exportar datos
function exportarDatos(format) {
    fetch('/api/datos')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                mostrarNotificacion(data.error, 'error');
                return;
            }
            
            switch(format) {
                case 'json':
                    exportarJSON(data);
                    break;
                case 'csv':
                    exportarCSV(data);
                    break;
                default:
                    mostrarNotificacion('Formato no soportado', 'warning');
            }
        })
        .catch(error => {
            console.error('Error exportando datos:', error);
            mostrarNotificacion('Error exportando datos', 'error');
        });
}

function exportarJSON(data) {
    const dataStr = JSON.stringify(data, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);
    const exportFileDefaultName = 'iguana_datos_' + new Date().toISOString().split('T')[0] + '.json';
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    document.body.appendChild(linkElement);
    linkElement.click();
    document.body.removeChild(linkElement);
    
    mostrarNotificacion('Datos exportados como JSON', 'success');
}

function exportarCSV(data) {
    // Convertir datos a CSV
    const headers = ['Individuo', 'Peso (kg)', 'Edad', 'Sexo', 'Fecha'];
    const rows = data.datos.map(item => [
        item.Individuos || '',
        item.Peso_Kg || '',
        item.Edad || '',
        item.Sexo || '',
        item.Fecha_entrga_CAV || ''
    ]);
    
    const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', 'iguana_datos_' + new Date().toISOString().split('T')[0] + '.csv');
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    mostrarNotificacion('Datos exportados como CSV', 'success');
}

// Descargar gráfico como imagen
function descargarGrafico(chartId, format) {
    const chartDiv = document.getElementById(chartId);
    if (!chartDiv) {
        mostrarNotificacion('Gráfico no encontrado', 'error');
        return;
    }
    
    Plotly.downloadImage(chartDiv, {
        format: format,
        filename: `iguana_${chartId}_${new Date().toISOString().split('T')[0]}`,
        height: 600,
        width: 800,
        scale: 2
    });
    
    mostrarNotificacion(`Gráfico descargado como ${format.toUpperCase()}`, 'success');
}

// Mostrar notificaciones
function mostrarNotificacion(mensaje, tipo = 'info') {
    const tipos = {
        'success': { class: 'alert-success', icon: 'check-circle' },
        'error': { class: 'alert-danger', icon: 'exclamation-circle' },
        'warning': { class: 'alert-warning', icon: 'exclamation-triangle' },
        'info': { class: 'alert-info', icon: 'info-circle' }
    };
    
    const tipoConfig = tipos[tipo] || tipos.info;
    
    // Crear elemento de notificación
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert ${tipoConfig.class} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${tipoConfig.icon} me-2"></i>
            <span class="flex-grow-1">${mensaje}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(alertDiv);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Animaciones de elementos
function animarElementos() {
    // Animar cards con delay escalonado
    const cards = document.querySelectorAll('.card:not(.animate-fade-in)');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('animate-fade-in');
        }, index * 100);
    });
    
    // Animar elementos con clase animate-on-scroll cuando son visibles
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-slide-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// Cambiar tema (claro/oscuro)
function toggleTema() {
    const body = document.body;
    const temaActual = body.getAttribute('data-bs-theme') || 'light';
    const nuevoTema = temaActual === 'dark' ? 'light' : 'dark';
    
    body.setAttribute('data-bs-theme', nuevoTema);
    localStorage.setItem('tema-preferido', nuevoTema);
    
    mostrarNotificacion(`Tema cambiado a ${nuevoTema === 'dark' ? 'oscuro' : 'claro'}`, 'info');
}

// Cargar tema guardado
function cargarTemaGuardado() {
    const temaGuardado = localStorage.getItem('tema-preferido');
    if (temaGuardado) {
        document.body.setAttribute('data-bs-theme', temaGuardado);
    }
}

// Inicializar tema al cargar
cargarTemaGuardado();

// Función para filtrar datos (ejemplo)
function filtrarDatos(filtros) {
    console.log('Aplicando filtros:', filtros);
    // Implementar lógica de filtrado según necesidad
}

// Función para buscar en datos
function buscarEnDatos(termino) {
    console.log('Buscando:', termino);
    // Implementar lógica de búsqueda
}

// Redimensionar gráficos al cambiar tamaño de ventana
let resizeTimer;
window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
        // Re-dibujar gráficos Plotly si existen
        if (typeof Plotly !== 'undefined') {
            Plotly.Plots.resize(document.getElementById('grafico-composicion'));
            Plotly.Plots.resize(document.getElementById('grafico-sexo'));
            Plotly.Plots.resize(document.getElementById('grafico-pesos'));
            Plotly.Plots.resize(document.getElementById('grafico-boxplot'));
        }
    }, 250);
});
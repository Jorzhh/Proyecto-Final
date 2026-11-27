/**
 * Práctica 06 – Cliente API REST
 * Consumo asíncrono de la API FlightPHP
 */

const configuredApi = (import.meta.env.VITE_API_BASE || '').trim();
const localApi = import.meta.env.DEV ? 'http://127.0.0.1:8086/api' : '';
const API_BASE = (configuredApi || localApi).replace(/\/+$/, '');
window.API_BASE = API_BASE;

window.setBioMode = (demo, detail = '') => {
    window.APP_MODE = demo ? 'demo' : 'live';
    const status = document.getElementById('api-status-text');
    const banner = document.getElementById('demo-mode-banner');
    if (status) {
        status.textContent = demo ? 'Sin backend · Modo demo' : 'Conectada · FlightPHP/MySQL';
        status.style.color = demo ? '#ffa726' : '#a8f060';
    }
    if (banner) {
        banner.hidden = !demo;
        banner.textContent = demo
            ? `MODO DEMO · ${detail || 'Datos precargados para explorar sin conexión al backend.'}`
            : '';
    }
};

async function checkHealth() {
    if (!API_BASE) return false;
    const apiOrigin = API_BASE.replace(/\/api\/?$/i, '');
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 4000);
    try {
        const response = await fetch(`${apiOrigin}/health`, {
            signal: controller.signal,
            cache: 'no-store',
            headers: { Accept: 'application/json' }
        });
        return response.ok;
    } catch {
        return false;
    } finally {
        clearTimeout(timeout);
    }
}

// ============================================================
// Helper genérico fetch + manejo de errores
// ============================================================
async function apiFetch(endpoint, options = {}) {
    if (!API_BASE) {
        throw new Error('No hay URL HTTPS de backend configurada; usa el modo demo precargado.');
    }
    const url = `${API_BASE}${endpoint}`;
    const headers = new Headers(options.headers || {});
    headers.set('Accept', 'application/json');
    if (options.body && !headers.has('Content-Type')) {
        headers.set('Content-Type', 'application/json');
    }
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    const merged = { ...options, headers, signal: options.signal || controller.signal };
    
    try {
        const response = await fetch(url, merged);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP ${response.status}`);
        }
        return data;
    } catch (error) {
        console.error(`[API Error] ${endpoint}:`, error.message);
        throw error;
    } finally {
        clearTimeout(timeout);
    }
}

// ============================================================
// ESPECIES
// ============================================================
async function getEspecies() {
    const res = await apiFetch('/especies');
    return res.data;
}

async function getEspecie(id) {
    const res = await apiFetch(`/especies/${id}`);
    return res.data;
}

// ============================================================
// SIMULACIONES
// ============================================================
async function getSimulaciones() {
    const res = await apiFetch('/simulaciones');
    return res.data;
}

async function getSimulacion(id) {
    const res = await apiFetch(`/simulaciones/${id}`);
    return res.data;
}

async function crearSimulacion(datos) {
    const res = await apiFetch('/simulaciones', {
        method: 'POST',
        body: JSON.stringify(datos),
    });
    return res.data;
}

async function actualizarSimulacion(id, datos) {
    const res = await apiFetch(`/simulaciones/${id}`, {
        method: 'PUT',
        body: JSON.stringify(datos),
    });
    return res;
}

async function eliminarSimulacion(id) {
    return await apiFetch(`/simulaciones/${id}`, { method: 'DELETE' });
}

// ============================================================
// MEDICIONES
// ============================================================
async function getMediciones(simId) {
    const res = await apiFetch(`/simulaciones/${simId}/mediciones`);
    return res.data;
}

async function guardarMedicion(datos) {
    const res = await apiFetch('/mediciones', {
        method: 'POST',
        body: JSON.stringify(datos),
    });
    return res.data;
}

async function guardarMedicionesBatch(mediciones) {
    const res = await apiFetch('/mediciones/batch', {
        method: 'POST',
        body: JSON.stringify({ mediciones }),
    });
    return res;
}

// ============================================================
// DECISIONES
// ============================================================
async function getDecisiones(simId) {
    const res = await apiFetch(`/simulaciones/${simId}/decisiones`);
    return res.data;
}

async function guardarDecision(datos) {
    const res = await apiFetch('/decisiones', {
        method: 'POST',
        body: JSON.stringify(datos),
    });
    return res.data;
}

// ============================================================
// REPORTES
// ============================================================
async function getTopBiomasa() {
    const res = await apiFetch('/reportes/top-biomasa');
    return res.data;
}

async function getEficiencia() {
    const res = await apiFetch('/reportes/eficiencia');
    return res.data;
}

async function getPromedioMadurez() {
    const res = await apiFetch('/reportes/promedio-madurez');
    return res.data;
}

async function compararSimulaciones(id1, id2) {
    const res = await apiFetch(`/reportes/comparar/${id1}/${id2}`);
    return res.data;
}

// Exportar para uso global
window.API = {
    checkHealth,
    getEspecies, getEspecie,
    getSimulaciones, getSimulacion, crearSimulacion, actualizarSimulacion, eliminarSimulacion,
    getMediciones, guardarMedicion, guardarMedicionesBatch,
    getDecisiones, guardarDecision,
    getTopBiomasa, getEficiencia, getPromedioMadurez, compararSimulaciones
};

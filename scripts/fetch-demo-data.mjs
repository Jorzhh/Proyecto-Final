import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const output = resolve(root, 'public/data/demo.json');
const textureOutput = resolve(root, 'public/textures/earth_atmos_2048.jpg');
const sites = [
  { id: 'guatemala', name: 'Guatemala', country: 'Guatemala', lat: 14.291, lon: -89.895 },
  { id: 'cordoba', name: 'Córdoba', country: 'España', lat: 37.888, lon: -4.779 },
  { id: 'oaxaca', name: 'Oaxaca', country: 'México', lat: 17.073, lon: -96.726 },
  { id: 'nairobi', name: 'Nairobi', country: 'Kenia', lat: -1.292, lon: 36.822 },
  { id: 'brasilia', name: 'Brasilia', country: 'Brasil', lat: -15.794, lon: -47.882 }
];
const speciesNames = [
  'Zea mays',
  'Phaseolus vulgaris',
  'Solanum lycopersicum',
  'Plumeria rubra',
  'Arabidopsis thaliana'
];

const sleep = milliseconds => new Promise(resolveSleep => setTimeout(resolveSleep, milliseconds));

async function getJson(url) {
  const response = await fetch(url, {
    headers: { accept: 'application/json', 'user-agent': 'ProyectoFinal-Observatorio/1.0 (educational demo)' },
    signal: AbortSignal.timeout(35_000)
  });
  if (!response.ok) throw new Error(`${response.status} ${response.statusText} en ${new URL(url).hostname}`);
  return response.json();
}

function average(values) {
  const valid = values.map(Number).filter(Number.isFinite);
  return valid.length ? Number((valid.reduce((sum, value) => sum + value, 0) / valid.length).toFixed(2)) : null;
}

function total(values) {
  const valid = values.map(Number).filter(Number.isFinite);
  return valid.length ? Number(valid.reduce((sum, value) => sum + value, 0).toFixed(2)) : null;
}

function dateString(date) {
  return date.toISOString().slice(0, 10);
}

const end = new Date();
end.setUTCDate(end.getUTCDate() - 14);
const start = new Date(end);
start.setUTCDate(start.getUTCDate() - 364);
const period = { start: dateString(start), end: dateString(end) };

const taxonMatches = {};
for (const name of speciesNames) {
  const match = await getJson(`https://api.gbif.org/v1/species/match?name=${encodeURIComponent(name)}`);
  const key = match.usageKey ?? match.speciesKey;
  if (!key) throw new Error(`GBIF no encontró una coincidencia taxonómica para ${name}.`);
  taxonMatches[name] = { taxonKey: key, scientificName: match.scientificName ?? name };
}

const outputSites = [];
for (const site of sites) {
  console.log(`Consultando clima y ocurrencias: ${site.name}`);
  const archiveQuery = new URLSearchParams({
    latitude: String(site.lat),
    longitude: String(site.lon),
    start_date: period.start,
    end_date: period.end,
    daily: 'temperature_2m_mean,precipitation_sum,shortwave_radiation_sum',
    timezone: 'UTC'
  });
  const archive = await getJson(`https://archive-api.open-meteo.com/v1/archive?${archiveQuery}`);
  const daily = archive.daily ?? {};
  if (!Array.isArray(daily.time) || daily.time.length < 300) {
    throw new Error(`Open-Meteo devolvió menos de 300 días para ${site.name}; revisa el periodo disponible.`);
  }

  const occurrences = {};
  for (const scientificName of speciesNames) {
    const taxon = taxonMatches[scientificName];
    const occurrenceQuery = new URLSearchParams({
      taxonKey: String(taxon.taxonKey),
      decimalLatitude: `${Math.max(-90, site.lat - 0.5)},${Math.min(90, site.lat + 0.5)}`,
      decimalLongitude: `${site.lon - 0.5},${site.lon + 0.5}`,
      hasCoordinate: 'true',
      limit: '20',
      offset: '0'
    });
    const raw = await getJson(`https://api.gbif.org/v1/occurrence/search?${occurrenceQuery}`);
    occurrences[scientificName] = {
      fuente: 'GBIF Occurrence API',
      nombre_consultado: scientificName,
      nombre_aceptado: taxon.scientificName,
      taxonKey: taxon.taxonKey,
      disponible: true,
      total: Number(raw.count ?? 0),
      puntos: (raw.results ?? [])
        .filter(record => Number.isFinite(Number(record.decimalLatitude)) && Number.isFinite(Number(record.decimalLongitude)))
        .map(record => ({
          lat: Number(record.decimalLatitude),
          lon: Number(record.decimalLongitude),
          fecha: record.eventDate ?? null,
          pais: record.country ?? null
        })),
      limite_mostrado: (raw.results ?? []).filter(record => record.decimalLatitude != null && record.decimalLongitude != null).length,
      nota_espacial: 'Total de GBIF dentro de una ventana rectangular aproximada de 1° × 1°; el número de puntos guardados está limitado a 20.'
    };
    await sleep(250);
  }

  console.log(`Consultando SoilGrids: ${site.name}`);
  const soilQuery = new URLSearchParams({ lon: String(site.lon), lat: String(site.lat), depth: '0-5cm', value: 'mean' });
  for (const property of ['clay', 'sand', 'soc', 'phh2o']) soilQuery.append('property', property);
  const soilRaw = await getJson(`https://rest.isric.org/soilgrids/v2.0/properties/query?${soilQuery}`);
  const soilProperties = {};
  for (const layer of soilRaw.properties?.layers ?? []) {
    soilProperties[layer.name] = {
      valor: layer.depths?.[0]?.values?.mean ?? null,
      unidad: layer.unit_measure?.mapped_units ?? layer.unit_measure?.target_units ?? null
    };
  }
  if (!['clay', 'sand', 'phh2o'].every(key => Number.isFinite(Number(soilProperties[key]?.valor)))) {
    throw new Error(`SoilGrids no entregó arcilla, arena y pH para ${site.name}; no se guardará una muestra incompleta.`);
  }

  outputSites.push({
    ...site,
    clima: {
      fuente: 'Open-Meteo Historical Weather API',
      periodo: period,
      dias: daily.time.length,
      temperatura_media_c: average(daily.temperature_2m_mean ?? []),
      precipitacion_total_mm: total(daily.precipitation_sum ?? []),
      radiacion_media_mj_m2_dia: average(daily.shortwave_radiation_sum ?? [])
    },
    suelo: {
      coordenadas: { lat: site.lat, lon: site.lon },
      fuente: 'ISRIC SoilGrids v2.0',
      profundidad: '0-5 cm',
      propiedades: soilProperties,
      atribucion: 'ISRIC SoilGrids'
    },
    ocurrencias: occurrences
  });

  // SoilGrids solicita no más de cinco consultas por minuto.
  if (site !== sites.at(-1)) await sleep(12_500);
}

const demo = {
  schema_version: 1,
  generated_at: new Date().toISOString(),
  demo_default_species: 'Zea mays',
  period,
  attribution: {
    globe: 'Textura terrestre del repositorio oficial de ejemplos Three.js: https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg',
    climate: 'Open-Meteo Historical Weather API: https://open-meteo.com/en/docs/historical-weather-api',
    soil: 'ISRIC SoilGrids v2.0: https://www.isric.org/explore/soilgrids',
    biodiversity: 'GBIF occurrence data: https://www.gbif.org/occurrence/search',
    notice: 'Los conteos y registros de GBIF describen datos publicados por sus proveedores; cero registros no demuestra ausencia de la especie. Las propiedades de suelo son predicciones globales a 0-5 cm, no un análisis de parcela.'
  },
  locations: outputSites
};

await mkdir(dirname(output), { recursive: true });
await mkdir(dirname(textureOutput), { recursive: true });
console.log('Descargando la textura del globo para incluirla en el paquete offline…');
const textureResponse = await fetch('https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg', {
  signal: AbortSignal.timeout(35_000)
});
if (!textureResponse.ok) throw new Error(`No se pudo descargar la textura terrestre: HTTP ${textureResponse.status}`);
await writeFile(textureOutput, Buffer.from(await textureResponse.arrayBuffer()));
await writeFile(output, `${JSON.stringify(demo, null, 2)}\n`, 'utf8');
console.log(`Archivo demo listo: ${output} (${outputSites.length} ubicaciones).`);

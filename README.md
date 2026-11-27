# Proyecto Final del Observatorio Global de Cultivos

Este proyecto convierte el laboratorio de la Práctica 6 en una aplicación HTML5 que se puede subir a itch.io. El ZIP de itch.io contiene solo el cliente estático; FlightPHP y MariaDB/MySQL viven en un servidor HTTPS aparte. Si ese servidor no responde, el Observatorio utiliza cinco muestras geográficas reales guardadas en `public/data/demo.json` y lo indica en pantalla.

La carpeta de la Práctica 6 se conserva por separado. `README_P06.md` guarda una copia de su documentación anterior para preparar el video de esa práctica.

## Estado de publicación

El código local, el modo demo y el build están preparados en esta carpeta. La dirección real de `/health`, el ZIP subido a itch.io, las capturas dentro del iframe y las pruebas con dos personas requieren una cuenta del hosting y del usuario. No se deben presentar esos pasos como completados hasta tener evidencia.

Hosting seleccionado para probar: **Alwaysdata Free**. Su plan gratuito actual ofrece PHP, MariaDB compatible con MySQL y HTTPS en su subdominio `alwaysdata.net`; publica límites modestos de recursos y suspende perfiles gratuitos inactivos. El backend todavía necesita una cuenta y una URL real para probarlo desde itch.io. Consulta [planes actuales](https://www.alwaysdata.com/en/offers/), [bases MariaDB/MySQL](https://help.alwaysdata.com/en/docs/web-hosting/databases/mariadb/), [PHP](https://help.alwaysdata.com/en/docs/web-hosting/languages/php/configuration/) y [certificados HTTPS](https://help.alwaysdata.com/en/docs/web-hosting/sites/ssl-tls/lets-encrypt/).

## Cómo funciona

1. **Frontend:** `public/index.html`, CSS y JavaScript muestran el simulador de crecimiento, los gráficos y el globo Three.js. Vite empaqueta localmente Three.js, OrbitControls y Chart.js.
2. **Cliente API:** `public/js/api-client.js` toma `VITE_API_BASE`. En desarrollo usa `http://127.0.0.1:8086/api`; en el build, si no se configura un backend HTTPS, activa el modo demo.
3. **API PHP:** `api/index.php` atiende rutas REST de FlightPHP y define `/health`. `api/geo-routes.php` consulta Open-Meteo, NASA POWER, SoilGrids e GBIF desde el servidor, para que esos servicios no dependan del CORS de cada proveedor.
4. **MariaDB/MySQL:** guarda especies, simulaciones, mediciones, decisiones y la caché geoespacial. `/health` devuelve `200` si puede comprobar la conexión y `503` si la base de datos no está disponible.
5. **Respaldo:** `public/data/demo.json` contiene cinco muestras. Si la API no está configurada o no responde, el Observatorio toma la ubicación demo más cercana e informa su nombre y distancia.

El índice de idoneidad es un **indicador didáctico**, no una recomendación agronómica certificada: combina temperatura (25%), precipitación (25%), pH (20%), textura (20%) y ocurrencias GBIF (10%) cuando esas variables están disponibles. La precipitación no mide humedad del sustrato. SoilGrids ofrece estimaciones globales a 0–5 cm, no un análisis de una parcela. La ausencia de ocurrencias GBIF no prueba que una especie no exista en el sitio.

## Fuentes y procedencia de la muestra demo

El archivo fue creado el **27 de noviembre de 2026** ejecutando `node scripts/fetch-demo-data.mjs`:

| Ubicación | Coordenadas | Datos guardados |
| --- | --- | --- |
| Guatemala, Guatemala | 14.291, -89.895 | Promedios y suma de precipitación de 365 días; SoilGrids; conteos GBIF de cinco especies |
| Córdoba, España | 37.888, -4.779 | Mismas variables |
| Oaxaca, México | 17.073, -96.726 | Mismas variables |
| Nairobi, Kenia | -1.292, 36.822 | Mismas variables |
| Brasilia, Brasil | -15.794, -47.882 | Mismas variables |

El periodo climático exacto queda dentro de cada objeto `clima.periodo`. Para el suelo se guardan arcilla, arena, carbono orgánico y pH de 0–5 cm. Para GBIF se consulta una ventana aproximada de 1° × 1° por ubicación y especie; se guardan el conteo y un máximo de 20 puntos. El archivo también conserva los enlaces de atribución.

- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): sus datos API están bajo [CC BY 4.0](https://open-meteo.com/en/license); requiere atribución.
- [ISRIC SoilGrids](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html): predicciones con licencia CC BY 4.0. La API beta pide limitar el uso a cinco consultas por minuto; el generador respeta ese intervalo.
- [GBIF](https://techdocs.gbif.org/en/data-use/): las licencias varían por registro (CC0, CC BY o CC BY-NC). Consulta la ficha original antes de reutilizar registros individuales.
- El mapa terrestre incluido procede de los [ejemplos oficiales de Three.js](https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg). Three.js usa licencia MIT; revisa el crédito indicado en `demo.json` antes de redistribuir la textura.

## Requisitos

- Node.js 20.19 o posterior y Corepack/pnpm para instalar las dependencias del frontend.
- PHP 8.x con FlightPHP, PDO MySQL y cURL para correr el backend.
- XAMPP MySQL/MariaDB para guardar datos durante el desarrollo local.
- Cuenta de hosting con HTTPS, PHP 8.x, MariaDB/MySQL y llamadas cURL salientes para el servidor público.

El ZIP de itch.io **no necesita PHP, MySQL, Node.js ni claves API** para funcionar en modo demo.

## Desarrollo local

1. Instala Node.js 20.19 o posterior.
2. Abre una terminal en esta carpeta y ejecuta `corepack pnpm install` una sola vez para descargar las herramientas del proyecto.
3. Ejecuta `iniciar_servidores.bat`. Abre `http://localhost:3006`; el globo y el Observatorio quedan disponibles con los datos demo aunque no tengas MySQL, FlightPHP o XAMPP configurados.
4. Para conectar también la API local, instala FlightPHP dentro de `api/`, inicia MySQL en XAMPP e importa `database/schema.sql` y luego `database/seed.sql`. El archivo de inicio detecta automáticamente PHP y FlightPHP; si faltan, abre el modo demo y no se detiene.
5. MySQL sirve para guardar historial y consultar datos desde el backend local. El ZIP público de itch.io no necesita MySQL, PHP ni claves.

No abras `public/index.html` con doble clic. Los módulos del navegador y el build funcionan desde un servidor HTTP.

## Build de itch.io

Para generar el build con modo demo, deja `VITE_API_BASE` vacío. Para una publicación con backend en vivo, crea `.env.production` local con la URL HTTPS terminada en `/api`, por ejemplo `VITE_API_BASE=https://cuenta.alwaysdata.net/api`, y luego vuelve a generar el build. **No guardes contraseñas ni claves en variables `VITE_*`: Vite las copia al navegador.**

```powershell
corepack pnpm install
npm run build
npm run package:itch
```

El script crea `Proyecto-Final-itchio.zip`. Debe contener `index.html` directamente en la raíz, junto con `assets/`, `data/` y texturas. Comprueba eso antes de subirlo; no comprimas la carpeta `dist` como carpeta anidada. El build usa `base: './'`, minificación y sourcemaps apagados. Vite produce una carpeta estática y admite rutas relativas para una instalación embebida ([guía de build](https://vite.dev/guide/build.html), [opción `base`](https://vite.dev/config/shared-options.html)). itch.io requiere `index.html` dentro del ZIP, nombres con mayúsculas/minúsculas consistentes y puede mostrar la app en iframe o pantalla completa ([guía oficial HTML5](https://itch.io/docs/creators/html5)).

## Backend y CORS

En el hosting:

1. Crea una base MariaDB/MySQL y un sitio PHP 8.x cuyo directorio raíz sea `api/`.
2. Importa `database/schema.sql` y luego `database/seed.sql`.
3. Completa `api/config.local.example.php` en un archivo privado `api/config.local.php`, o configura las variables `DB_HOST`, `DB_NAME`, `DB_USER` y `DB_PASS` desde el panel. El archivo privado está excluido por `.gitignore`.
4. Publica la carpeta `api/` y verifica que `https://TU-SERVIDOR/health` devuelva JSON con HTTP 200 y `database: connected`.
5. En la configuración de CORS de `api/index.php`, el servidor permite el origen local de desarrollo y subdominios HTTPS `*.itch.zone`/`*.hwcdn.net`. El valor `Access-Control-Allow-Origin` se devuelve para el origen permitido específico; no se usa `*`.
6. En la consola del juego ya cargado dentro de itch.io, ejecuta `fetch('https://TU-SERVIDOR/health').then(r => r.json()).then(console.log)`. Guarda la captura solo si responde sin error de CORS.
7. Crea `.env.production` con la dirección real del backend y reconstruye el ZIP.

Encabezados configurados: `Access-Control-Allow-Origin` (origen exacto validado), `Vary: Origin`, `Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS`, `Access-Control-Allow-Headers: Content-Type, Authorization` y `Access-Control-Max-Age: 86400`. El navegador puede enviar una solicitud `OPTIONS` previa a las peticiones JSON; la API la contesta antes de ejecutar la ruta.

No uses InfinityFree como backend del iframe: el proveedor documenta que su sistema de seguridad bloquea llamadas AJAX/CORS desde otros dominios en el plan gratis ([limitaciones del sistema](https://forum.infinityfree.com/t/browser-security-system-features-and-limitations/49353)).

## Página y entregables

`PAGINA_ITCH_IO.md` contiene texto de producto, etiquetas, créditos, descripción de fuentes y ajustes de incrustación. Al publicar en itch.io:

- Selecciona **HTML Game** y sube `Proyecto-Final-itchio.zip`.
- Activa lanzamiento a pantalla completa, marca Mobile Friendly y conserva la adaptación al tamaño del iframe.
- Crea primero el borrador o acceso restringido; verifica después la vista integrada en desktop y celular.
- Crea el repositorio GitHub `proyecto-final-itchio`; sube código, README y configuración CORS. Adjunta el ZIP en una Release.
- Usa la portada ya preparada en `media/itch/portada-630x500.png` (630 × 500). Toma capturas reales y un GIF de 10–20 segundos dentro de itch.io; guarda también la evidencia del modo demo, `/health` y CORS.
- Pide a dos personas externas que usen la página y anota lo que sí hicieron, dónde dudaron y qué cambiarías. No inventes esas observaciones.

Cuando crees el repositorio vacío en GitHub, abre una terminal en `Proyecto Final`. Ejecuta estos comandos en orden. `git init -b main` prepara el repositorio local; si ya existe, Git conserva su contenido. Cambia `TU_USUARIO` por tu nombre de usuario de GitHub:

```powershell
git init -b main
git add .
git commit -m "Preparar Proyecto Final para itch.io"
git remote add origin https://github.com/TU_USUARIO/proyecto-final-itchio.git
git push -u origin main
```

Si Git solicita tu identidad, usa tu nombre y correo asociados a GitHub. El `.gitignore` excluye `node_modules/`, `dist/`, el ZIP y archivos privados como `.env.production` y `api/config.local.php`. Después adjunta `Proyecto-Final-itchio.zip` manualmente en la sección **Releases** del repositorio.

## Respuestas preparadas para la exposición

1. **¿Qué subiste a itch.io y qué no?** Subo el cliente HTML/CSS/JS y sus recursos; el servidor FlightPHP/MySQL va aparte porque itch.io aloja el contenido del navegador dentro de un iframe estático.
2. **¿Qué hosting elegiste?** La selección para validar es Alwaysdata Free porque documenta PHP, MariaDB y HTTPS. La URL todavía debe crearse y probarse; su plan es de recursos limitados y solo permite el subdominio del proveedor en el plan gratuito. No digas que ya quedó desplegado hasta obtener `/health`.
3. **¿Cómo viaja la información?** Navegador → iframe → cliente API → FlightPHP con HTTPS → cURL hacia la fuente pública → JSON de respuesta → caché de MariaDB → JSON al navegador. Si no hay respuesta, el frontend toma su muestra demo.
4. **¿Qué hiciste para CORS/mixed content?** Añadí validación de origen y respuesta OPTIONS para localhost y los subdominios de itch.io. El build usa el `https://` real del backend; el iframe no debe llamar a `http://`. La prueba final pendiente es correrla en la página de itch y guardar su captura.
5. **¿Cómo funciona demo y qué contiene?** Cinco ubicaciones, 365 días de clima de Open-Meteo, suelo SoilGrids a 0–5 cm y conteos GBIF para cinco especies. La app selecciona el punto demo más cercano. Es contexto global y no sustituye muestreo de parcela; cero GBIF no demuestra ausencia.
6. **¿Qué optimizaste?** Vite resuelve módulos, agrupa Three.js/Chart.js, minifica y genera rutas relativas; se desactivan sourcemaps. Registra en la tabla de abajo el tamaño y archivos de `dist` al hacer el build final.
7. **¿Cómo evitaste publicar secretos?** No hay API keys del cliente. La URL del servidor es pública, no es una contraseña. `.env.production` y `api/config.local.php` están ignorados por Git; los datos de acceso quedan solo en el panel o archivo privado del servidor.
8. **¿Qué decisiones tomaste en itch.io?** El título explica el producto y la descripción dice en una frase qué integra: simulación 3D, clima, suelo y biodiversidad global. Se añadirán etiquetas de agricultura, ciencia, simulación, Web y Three.js junto con créditos y licencias.
9. **¿Cómo responde en móvil y pantalla completa?** El CSS tiene puntos de adaptación para pantallas estrechas; itch ofrece su control de pantalla completa. Aún hay que comprobar el ZIP real dentro del iframe en celular y escritorio.
10. **¿Qué dijeron dos personas externas?** Completa la respuesta después de observarlas. Pídeles encontrar una ubicación, leer un indicador y usar las condiciones en la simulación; anota sus dudas sin sugerirles los pasos.
11. **¿Cómo automatizarías versiones?** Un GitHub Actions puede ejecutar instalación limpia, build y empaquetado al crear un tag `v1.1.0`; Butler puede publicar el ZIP usando un secreto `BUTLER_API_KEY`, nunca guardado en el repositorio.
12. **¿Qué aporta itch.io frente a Pages, Netlify o servidor propio?** Itch aporta ficha de producto, iframe y botón de pantalla completa; Pages/Netlify simplifican hosting estático y CI; un servidor propio es el que permite PHP y base de datos. Para esta arquitectura se usan itch para el frontend y un backend aparte.

### Métricas del build final

Llena esta tabla con el resultado de `npm run build` y el conteo de archivos de `dist`:

| Medición | Valor final |
| --- | --- |
| Archivos del build | 13 |
| Tamaño total del directorio `dist` | 1.41 MiB (1,473,555 bytes) |
| Tamaño del ZIP de itch.io | 749.8 KiB (767,829 bytes) |

## Video de la Práctica 6

La versión original de `Practica6` no se mezcla con esta copia. Para el video de esa práctica, abre la versión original y recorre: (1) selección de cultivo y ambiente; (2) globo, rotación y consulta de coordenadas; (3) simulación día por día y crecimiento de la planta; (4) KPIs y gráficos; (5) comparación A/B; (6) historial y reportes mostrando qué depende de MySQL. Si MySQL no inicia, explica que la simulación local y los datos demo pueden seguir, pero los guardados del historial dependen de la base.

Para el video del proyecto final, muestra después el banner demo, la ubicación más cercana, los créditos/fuentes y el flujo de tres capas. Encontrarás el guion completo y las respuestas para explicar en `GUIA_PARA_PRESENTAR_FINAL.docx`.

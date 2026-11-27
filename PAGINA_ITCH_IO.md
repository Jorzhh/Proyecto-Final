# Texto para la página de itch.io

## Ficha

**Título:** BioLab 3D: Observatorio Global de Cultivos  
**Tipo de proyecto:** HTML Game  
**Precio:** Gratis / No payments  
**Tags:** Educational, Science, Simulation, Agriculture, 3D, Browser, Three.js  
**Estado inicial:** Borrador o restringido mientras se verifica en iframe y móvil  
**Portada:** `media/cover-itch-630x500.png` (630 × 500 px)  
**GIF:** `media/observatorio-demo.gif` (10–20 s, en preparación)  

## Descripción breve

Explora clima, suelo y biodiversidad de cultivos en un globo 3D y usa esas condiciones como punto de partida para una simulación de crecimiento.

## Descripción para pegar en itch.io

### ¿Qué puedes explorar?

BioLab 3D es un observatorio educativo para relacionar una especie de cultivo con su entorno. Rota el globo, elige una especie, selecciona una ubicación y consulta información climática, propiedades globales de suelo y registros de biodiversidad publicados en GBIF.

Después puedes pasar las condiciones disponibles al simulador 3D de crecimiento y observar cómo cambian la planta, sus indicadores y sus gráficas cuando modificas el ambiente. La vista también incluye comparación geográfica A/B.

### Cómo usarlo

1. Entra a **Globo** y gira o acerca el planeta.
2. Selecciona una especie del catálogo y una ubicación de ejemplo, o introduce una coordenada.
3. Pulsa **Consultar esta ubicación** para ver las variables disponibles y la idoneidad orientativa.
4. Pulsa **Usar condiciones en la simulación** para pasar algunas variables a la vista de cultivo.
5. En **Cultivo**, ajusta temperatura, agua, luz y nutrientes; inicia la simulación y observa la planta, el progreso y las gráficas.
6. En **A/B Test**, compara dos especies o condiciones para observar cómo cambia la trayectoria de crecimiento.

### Datos y límites

El modo en vivo usa fuentes públicas mediante una API PHP. Si el backend no está disponible, el proyecto usa muestras guardadas de cinco ubicaciones y muestra un aviso **Modo demo**. La ubicación de respaldo es la muestra más cercana; puede estar a kilómetros del punto seleccionado.

Las capas globales de clima y suelo son contexto de escala amplia. El pH, la textura y el índice se deben confirmar con datos de la parcela antes de tomar decisiones. Un conteo GBIF describe registros publicados y no mide la ausencia de una especie.

### Créditos

Proyecto final realizado en clase con el profesor **José Luis David Bonilla Carranza**.  
Desarrollo: **Humberto Josué Orozco Espinosa** e **Irlanda Goreti Álvarez Lomeli**.  
Tecnologías: Three.js, Vite, Chart.js, FlightPHP, PHP y MariaDB/MySQL.  
Fuentes: Open-Meteo, NASA POWER, ISRIC SoilGrids y GBIF. Consulta las atribuciones y licencias detalladas en el repositorio.

## Ajustes de incrustación

- Habilita la opción **Click to launch in fullscreen** (o el botón de fullscreen si se elige “Embed in page”).
- Marca **Mobile Friendly** después de probar la versión real en celular.
- Mantén **Click to Play** si itch.io lo recomienda para reducir el trabajo inicial del navegador.
- La app usa `100vw × 100vh`, canvas responsivo y `base: './'`; aun así, hay que confirmar su ajuste dentro del iframe de itch.io.
- Comparte la URL de prueba restringida con el profesor antes de hacerla pública.

## Imágenes y accesibilidad

La portada ya está preparada en `media/itch/portada-630x500.png` con el tamaño recomendado de 630 × 500 px. Súbela en las imágenes de la página. Guarda capturas reales del cultivo y el globo en `media/screens/`, y un GIF de 10–20 segundos. Esos tres elementos quedan pendientes hasta probar el build dentro del iframe real de itch.io; no presentes una captura local como evidencia del iframe. Añade texto alternativo descriptivo, por ejemplo “Globo 3D con una ubicación agrícola marcada y paneles de clima, suelo y registros GBIF”.

## Borrador de devlog

### Versión 1.0 · Del laboratorio local al observatorio web

Separamos el frontend estático del backend FlightPHP/MariaDB, generamos un build con Vite y añadimos un modo demo con datos precargados de cinco ubicaciones. El globo incluye la textura local y las bibliotecas 3D y de gráficas quedan en el build. En el backend añadimos `/health` y la política CORS para probar el iframe HTTPS de itch.io. Próximo paso: publicar el backend, verificar `/health` desde el iframe y registrar pruebas con dos personas.

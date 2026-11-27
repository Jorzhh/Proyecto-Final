from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from pathlib import Path

OUT = Path("GUIA_PARA_PRESENTAR_FINAL.docx")
doc = Document()
sec = doc.sections[0]
sec.top_margin = Inches(0.62)
sec.bottom_margin = Inches(0.62)
sec.left_margin = Inches(0.72)
sec.right_margin = Inches(0.72)
sec.header_distance = Inches(0.3)
sec.footer_distance = Inches(0.3)

GREEN = "2E7D32"
DARK = "173323"
MUTED = "52665A"
PALE = "EAF4EA"
PALEBLUE = "EAF3F5"
WHITE = "FFFFFF"
BLACK = "1C2920"
ORANGE = "A85C12"

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Arial"
normal.font.size = Pt(10)
normal.font.color.rgb = RGBColor.from_string(BLACK)
normal.paragraph_format.space_after = Pt(5)
normal.paragraph_format.line_spacing = 1.08

for name, size, color in [("Title", 26, DARK), ("Heading 1", 17, DARK), ("Heading 2", 12, GREEN), ("Heading 3", 10, GREEN)]:
    s = styles[name]
    s.font.name = "Arial"
    s.font.size = Pt(size)
    s.font.bold = True
    s.font.color.rgb = RGBColor.from_string(color)
    s.paragraph_format.keep_with_next = True
    s.paragraph_format.space_before = Pt(8 if name != "Title" else 0)
    s.paragraph_format.space_after = Pt(5)

# Word's built-in Title style can carry a default bottom rule. Keep the
# requested Title style while explicitly removing that decorative border.
title_ppr = styles["Title"]._element.get_or_add_pPr()
title_border = title_ppr.find(qn("w:pBdr"))
if title_border is not None:
    title_ppr.remove(title_border)

# Header/footer
header = sec.header.paragraphs[0]
header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
run = header.add_run("BIO LAB 3D   |   PROYECTO FINAL")
run.bold = True
run.font.name = "Arial"
run.font.size = Pt(8)
run.font.color.rgb = RGBColor.from_string(GREEN)
footer = sec.footer.paragraphs[0]
footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = footer.add_run("Guía de exposición   •   ")
r.font.size = Pt(8)
r.font.color.rgb = RGBColor.from_string(MUTED)
field = OxmlElement("w:fldSimple")
field.set(qn("w:instr"), "PAGE")
footer._p.append(field)

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def cell_text(cell, text, bold=False, color=BLACK, size=9):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "Arial"
    r.font.size = Pt(size)
    r.font.color.rgb = RGBColor.from_string(color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

def table(rows, widths=None):
    t = doc.add_table(rows=0, cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci, val in enumerate(row):
            if widths:
                cells[ci].width = Inches(widths[ci])
            cell_text(cells[ci], val, bold=(ri == 0), color=(WHITE if ri == 0 else BLACK), size=8.8)
            if ri == 0:
                shade(cells[ci], DARK)
            elif ri % 2 == 0:
                shade(cells[ci], "F2F7F2")
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return t

def p(text="", bold_start=None, color=None, size=None, italic=False):
    para = doc.add_paragraph()
    if bold_start and text.startswith(bold_start):
        a = para.add_run(bold_start)
        a.bold = True
        b = para.add_run(text[len(bold_start):])
        runs = [a, b]
    else:
        runs = [para.add_run(text)]
    for r in runs:
        r.font.name = "Arial"
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
        if size:
            r.font.size = Pt(size)
        if italic:
            r.italic = True
    return para

def bullet(text):
    para = doc.add_paragraph(style="List Bullet")
    para.paragraph_format.left_indent = Inches(0.22)
    para.paragraph_format.first_line_indent = Inches(-0.13)
    para.paragraph_format.space_after = Pt(3)
    para.add_run(text)
    return para

LIST_NUMBER = 0
def reset_numbered():
    global LIST_NUMBER
    LIST_NUMBER = 0

def numbered(text):
    global LIST_NUMBER
    LIST_NUMBER += 1
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Inches(0.25)
    para.paragraph_format.first_line_indent = Inches(-0.15)
    para.paragraph_format.space_after = Pt(4)
    lead = para.add_run(f"{LIST_NUMBER}. ")
    lead.bold = True
    lead.font.color.rgb = RGBColor.from_string(GREEN)
    para.add_run(text)
    return para

def callout(label, text, fill=PALE):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    shade(c, fill)
    c.text = ""
    para = c.paragraphs[0]
    para.paragraph_format.space_after = Pt(4)
    rr = para.add_run(label + "\n")
    rr.bold = True
    rr.font.name = "Arial"
    rr.font.color.rgb = RGBColor.from_string(GREEN)
    rr.font.size = Pt(9)
    rr = para.add_run(text)
    rr.font.name = "Arial"
    rr.font.size = Pt(9.5)
    rr.font.color.rgb = RGBColor.from_string(BLACK)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)

def page():
    doc.add_page_break()

# Page 1
doc.add_paragraph("Guía para presentar el Proyecto Final", style="Title")
sub = doc.add_paragraph()
sub.paragraph_format.space_after = Pt(12)
rr = sub.add_run("Observatorio Global de Cultivos · explicación paso a paso")
rr.font.name = "Arial"
rr.font.size = Pt(13)
rr.font.color.rgb = RGBColor.from_string(GREEN)

callout("Idea principal", "La Práctica 6 se conserva aparte para su propio video. El Proyecto Final es una copia preparada para publicarse: la página puede mostrar una demo sin conexión, y el backend PHP/MySQL se conecta por separado cuando esté desplegado.", PALEBLUE)

doc.add_heading("Qué ya está listo", level=1)
bullet("Una carpeta independiente llamada Proyecto Final, para que la Práctica 6 original siga disponible para tu video.")
bullet("El simulador y el globo empaquetados como una página estática; el ZIP tiene index.html en la raíz y contiene el archivo demo.")
bullet("Una muestra de cinco ubicaciones con datos públicos de clima, suelo y biodiversidad para que la vista global tenga contenido sin MySQL.")
bullet("Un lanzador local que intenta abrir primero la página y permite recorrer la demo aunque PHP, FlightPHP o MySQL no estén listos.")

doc.add_heading("Palabras que vas a escuchar", level=2)
table([
    ["Palabra", "Explicación sencilla"],
    ["Frontend", "La parte que ves y usas en el navegador: controles, simulación, gráficas y globo."],
    ["API", "El intermediario que recibe una petición de la página y busca o guarda datos en el servidor."],
    ["MySQL", "La base de datos; sirve para conservar información como historiales y registros."],
    ["Demo sin conexión", "Datos de ejemplo guardados junto con la página para que la función global no dependa de MySQL."],
    ["Build / ZIP", "La versión final comprimida que se puede subir como juego HTML5 a itch.io."],
], widths=[1.55, 5.75])

callout("Analogía para recordarlo", "Piensa en un vivero: el frontend es el mostrador que usa el visitante; la API es la persona que va a consultar; MySQL es el cuaderno donde se guardan las visitas; y el JSON demo es una carpeta de muestras preparada para cuando el mostrador no tenga internet.")

# Page 2
page()
doc.add_heading("Cómo recorrer la demo", level=1)
p("Haz la primera demostración desde la carpeta Proyecto Final. La página local usa el mismo paquete estático que se prepara para itch.io.")
reset_numbered()
numbered("La primera vez, instala Node.js y abre una terminal en Proyecto Final. Ejecuta: corepack pnpm install. Esto descarga las herramientas del frontend.")
numbered("Abre iniciar_servidores.bat. El navegador debe abrir http://localhost:3006. Si falta MySQL, PHP o FlightPHP, el lanzador deja disponible la demo sin conexión.")
numbered("En Observatorio Global, elige una de las ubicaciones o cambia las coordenadas. Pulsa Consultar esta ubicación para explicar los datos de muestra y la fuente.")
numbered("Mueve el globo con el mouse y señala que el punto representa una ubicación seleccionada. Explica que la app usa la muestra guardada más cercana, no un análisis de esa parcela.")
numbered("Abre Cultivo y recorre las condiciones del simulador, el avance por días, los indicadores y la gráfica. Compara dos condiciones si esa opción está activa.")
numbered("Muestra Historial/Reportes y aclara que guardar y recuperar registros necesita que el backend y MySQL estén conectados.")
numbered("Cierra con créditos y fuentes. Señala el aviso de demo para que quede claro cuándo son datos guardados y cuándo se consultaría una API en vivo.")

doc.add_heading("Guion breve para decirlo", level=2)
callout("Puedes explicarlo así", "“Primero voy a mostrar el Observatorio Global. Esta versión tiene cinco ubicaciones con datos públicos que ya guardé como demo. Al elegir una coordenada, la aplicación muestra la muestra más cercana; por eso sirve para demostrar la interfaz aunque no haya una base activa. Luego paso a la simulación de cultivo, donde cambio condiciones y observo cómo varían el crecimiento, los indicadores y la gráfica. El historial sí necesita la API y MySQL para guardar la información.”")

doc.add_heading("Si el navegador no abre", level=2)
bullet("Comprueba que Node.js esté instalado y que hayas ejecutado corepack pnpm install dentro de esta carpeta.")
bullet("Vuelve a abrir iniciar_servidores.bat y entra manualmente a http://localhost:3006.")
bullet("No abras public/index.html con doble clic: los módulos de JavaScript necesitan que la página salga desde un servidor local.")

# Page 3
page()
doc.add_heading("Cómo funciona por dentro", level=1)
table([
    ["Parte", "Qué hace", "Cómo explicarlo"],
    ["Página HTML/CSS/JS", "Muestra controles, globo, gráficos y simulación.", "Es la pantalla del visitante."],
    ["Three.js y Chart.js", "Dibujan el globo 3D y los gráficos dentro del navegador.", "Son bibliotecas de JavaScript que agregan visualizaciones."],
    ["Vite", "Junta los módulos y recursos, minimiza y arma la carpeta dist.", "Es la herramienta que prepara una versión ordenada y rápida para publicar."],
    ["FlightPHP", "Expone rutas REST, consulta servicios públicos y devuelve JSON.", "Es la puerta de entrada del servidor."],
    ["MariaDB/MySQL", "Guarda especies, datos y registros persistentes.", "Es el cuaderno que no se borra al cerrar el navegador."],
    ["demo.json", "Guarda valores de cinco puntos y habilita el modo de ejemplo.", "Es el respaldo que deja mostrar la página aun sin servidor."],
], widths=[1.5, 2.95, 2.85])

doc.add_heading("Camino de una consulta en vivo", level=2)
callout("Flujo de datos", "Navegador → frontend → API PHP por HTTPS → proveedor público y/o MySQL → respuesta JSON → pantalla. Si el backend no está disponible, la página toma demo.json y avisa que está en modo demo.", PALEBLUE)

doc.add_heading("Qué contiene la demo y qué no afirma", level=2)
bullet("Cinco ubicaciones de ejemplo: Guatemala, Córdoba, Oaxaca, Nairobi y Brasilia.")
bullet("Clima histórico de Open-Meteo, suelo estimado por SoilGrids a 0–5 cm y conteos de ocurrencias consultadas en GBIF.")
bullet("La muestra climática resume un periodo guardado de 365 días. GBIF puede mostrar cero registros por falta de datos; eso no prueba que la especie no exista.")
bullet("Los datos globales son contexto para aprender y explorar. No reemplazan una medición en una parcela ni constituyen una recomendación agrícola certificada.")
bullet("El backend, la URL HTTPS y la prueba CORS dentro del iframe de itch.io todavía requieren despliegue y acceso a las cuentas. Presenta esa parte como pendiente hasta tener evidencia.")

# Page 4
page()
doc.add_heading("Qué hacer para publicarlo", level=1)
p("GitHub y itch.io hacen trabajos distintos. GitHub conserva el código y las versiones; itch.io muestra la ficha y deja jugar el ZIP.")
table([
    ["Lugar", "Qué se sube", "Para qué sirve"],
    ["GitHub", "Código, README, scripts y documentación; ZIP en una Release.", "Revisar el código y conservar las versiones del proyecto."],
    ["itch.io", "Proyecto-Final-itchio.zip como juego HTML5.", "Abrir la página del juego y ejecutarlo en el navegador."],
    ["Hosting del backend", "La API PHP y su configuración privada.", "Dar datos en vivo, CORS, y conexión con MariaDB/MySQL."],
], widths=[1.45, 3.25, 2.6])

doc.add_heading("Pasos de publicación", level=2)
reset_numbered()
numbered("En Proyecto Final, prepara la versión con npm run package:itch. La orden compila el frontend y crea Proyecto-Final-itchio.zip.")
numbered("Crea en GitHub un repositorio llamado proyecto-final-itchio. Añade los archivos de Proyecto Final. El ZIP se adjunta como Release; node_modules y dist no son necesarios en el control de código.")
numbered("En itch.io, crea la página y elige HTML Game. Sube el ZIP y verifica que index.html aparezca en la raíz del archivo.")
numbered("Completa la portada de 630 × 500, capturas, GIF de 10–20 segundos, descripción, etiquetas, créditos y atribuciones de datos.")
numbered("Prueba la página en el iframe de itch.io en escritorio y en celular. Después pide a dos personas que prueben el flujo y anota observaciones reales.")
numbered("Para activar datos en vivo, despliega primero API y base de datos en un hosting HTTPS, revisa /health y CORS y vuelve a construir el ZIP con la URL pública.")

callout("El ZIP ya preparado", "Proyecto-Final-itchio.zip tiene index.html en la raíz, incluye data/demo.json y pesa aproximadamente 750 KiB. La publicación en itch.io y la prueba dentro de su iframe aún se hacen desde tu cuenta.", PALE)

doc.add_heading("Qué significa CORS", level=2)
p("El navegador limita que una página cargada desde itch.io lea respuestas de otro dominio. CORS es la lista de orígenes permitidos por el backend. El proyecto permite los subdominios HTTPS usados por itch.io, pero la prueba real se debe hacer cuando exista la dirección pública del servidor.")

# Page 5
page()
doc.add_heading("Preguntas que te pueden hacer", level=1)
table([
    ["Pregunta", "Respuesta en palabras sencillas"],
    ["¿Por qué usar una API?", "Para que el navegador no consulte y guarde todo por su cuenta. La API ordena esas peticiones y responde en un formato común."],
    ["¿Para qué sirve MySQL?", "Para conservar datos e historial. La demo estática puede mostrarse sin él; las funciones de guardado sí lo necesitan."],
    ["¿Por qué separamos página y servidor?", "itch.io sirve archivos estáticos dentro de un iframe. PHP y MySQL requieren otro hosting y se conectan por HTTPS."],
    ["¿Cómo evitan los errores de CORS?", "El backend responde con permisos para orígenes válidos de itch.io. Falta confirmar la respuesta desde el iframe publicado."],
    ["¿Cómo saben los datos demo?", "Se guardaron con la fecha, fuente, ubicación y licencia descritas en README.md y demo.json."],
    ["¿Qué limita el indicador?", "Es una combinación didáctica de variables globales; no es un diagnóstico de suelo o una recomendación para sembrar."],
    ["¿Qué falta terminar?", "Desplegar backend y base de datos, completar la ficha pública, probar el iframe y recoger la opinión de dos usuarios externos."],
], widths=[2.2, 5.1])

doc.add_heading("Presentación final en cinco momentos", level=2)
reset_numbered()
numbered("Problema y objetivo: explicar que reunimos simulación de cultivos y contexto global de clima, suelo y biodiversidad.")
numbered("Demostración: mostrar el globo, una ubicación, la etiqueta demo, el simulador, los indicadores y un gráfico.")
numbered("Arquitectura: contar el flujo frontend–API–base de datos y mencionar la alternativa local demo.")
numbered("Publicación: explicar que el ZIP estático va en itch.io y el código va en GitHub; el backend vive en un hosting HTTPS.")
numbered("Límites y cierre: dejar claro qué datos son de muestra y qué pruebas faltan antes de llamarlo producción.")

# Page 6
page()
doc.add_heading("Video separado de la Práctica 6", level=1)
callout("No mezcles las entregas", "Graba la Práctica 6 desde su carpeta original. Proyecto Final es una copia de trabajo para publicar; sus cambios no deben reemplazar la práctica que necesitas explicar.", PALEBLUE)

doc.add_heading("Orden para grabar la Práctica 6", level=2)
reset_numbered()
numbered("Presenta el nombre y el objetivo del laboratorio.")
numbered("Selecciona un cultivo y explica las variables iniciales.")
numbered("Muestra el simulador 3D y los controles de días o condiciones.")
numbered("Abre KPIs y gráficas; explica qué representa cada indicador.")
numbered("Muestra la comparación A/B y cambia solo una condición para que se note la diferencia.")
numbered("Recorre el globo y una consulta de ubicación, aclarando qué datos son de fuentes externas.")
numbered("Abre historial/reportes y explica que guardar depende de MySQL. Si no inicia, dilo de frente; no presentes el guardado como funcionando.")

doc.add_heading("Frase para explicar el problema de MySQL", level=2)
callout("Respuesta honesta", "“La simulación local puede recorrerse, pero MySQL almacena los registros persistentes. En esta computadora el servicio no arrancó, así que esa parte no pudo validarse. El Proyecto Final tiene una demo independiente para mostrar el Observatorio sin fingir que la base está conectada.”", PALE)

doc.add_heading("Checklist antes de exponer", level=2)
for text in [
    "Tengo abierta la carpeta correcta: Práctica 6 para ese video o Proyecto Final para la demo pública.",
    "Probé iniciar_servidores.bat y la dirección local http://localhost:3006.",
    "Sé decir si estoy mostrando demo o backend en vivo.",
    "Puedo explicar frontend, API, MySQL, demo.json, CORS y ZIP sin memorizar definiciones largas.",
    "No digo que la publicación, el hosting o las pruebas externas estén terminados sin capturas que lo demuestren.",
]:
    bullet(text)

doc.add_paragraph()
last = doc.add_paragraph("Usa esta guía como apoyo; adapta las frases a tu manera de hablar.")
last.alignment = WD_ALIGN_PARAGRAPH.CENTER
for rr in last.runs:
    rr.italic = True
    rr.font.color.rgb = RGBColor.from_string(MUTED)
    rr.font.size = Pt(9)

doc.core_properties.title = "Guía para presentar el Proyecto Final"
doc.core_properties.subject = "Explicación del Observatorio Global de Cultivos y preparación de la publicación"
doc.core_properties.author = "Proyecto Final BioLab 3D"
doc.save(OUT)
print(OUT.resolve())


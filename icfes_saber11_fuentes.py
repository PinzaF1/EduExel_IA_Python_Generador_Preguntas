# icfes_saber11_fuentes.py
# ------------------------------------------------------------
# Fuentes y descripciones oficiales de las pruebas Saber 11°
# Fuente principal:
#   ICFES - Evaluaciones Saber 11°
#   https://www.icfes.gov.co/evaluaciones-icfes/saber-11/
#
# Este módulo NO genera preguntas. Solo provee:
#   - Nombre oficial de cada prueba
#   - Descripción general por área
#   - Competencias clave / componentes
#   - Lista de fuentes documentales (URL oficiales)
# Para ser usado por EduExcel en prompts y metadatos.
# ------------------------------------------------------------

# Mapea el nombre de área que usas en EduExcel -> nombre oficial Saber 11°
ICFES_AREA_ALIAS = {
    "Lenguaje": "Lectura Crítica",           # Tu área "Lenguaje" ≈ prueba "Lectura Crítica"
    "Matemáticas": "Matemáticas",
    "Ciencias Naturales": "Ciencias Naturales",
    "Inglés": "Inglés",
    "sociales": "Sociales y Ciudadanas",     # Tu clave 'sociales'
}

ICFES_SABER11_FUENTES = {
    "Lectura Crítica": {
        "codigo_area": "LC",
        "descripcion": (
            "Evalúa la capacidad del estudiante para comprender, interpretar y evaluar textos "
            "que se encuentran en la vida cotidiana y en contextos académicos no especializados. "
            "Las preguntas se organizan en torno a tres competencias y se aplican sobre textos "
            "continuos y discontinuos."
        ),
        "competencias": [
            {
                "nombre": "Identificar y entender los contenidos locales",
                "descripcion": (
                    "Comprender el significado de palabras, expresiones y frases que aparecen "
                    "explícitamente en el texto."
                ),
            },
            {
                "nombre": "Comprender el sentido global del texto",
                "descripcion": (
                    "Reconocer cómo se articulan los elementos locales de un texto para construir "
                    "un sentido global coherente."
                ),
            },
            {
                "nombre": "Reflexionar a partir del texto y evaluar su contenido",
                "descripcion": (
                    "Adoptar una postura crítica frente al texto, valorar sus afirmaciones y "
                    "analizar su contenido."
                ),
            },
        ],
        "tipos_textos": {
            "continuos": [
                "Literarios (cuentos, novelas).",
                "Informativos (ensayos, artículos de prensa).",
                "Filosóficos (fragmentos argumentativos).",
            ],
            "discontinuos": [
                "Infografías.",
                "Cómics.",
                "Tablas.",
                "Gráficos.",
            ],
        },
        "fuentes": [
            {
                "tipo": "pagina_oficial",
                "titulo": "Saber 11° - ICFES",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": "Página oficial general del examen Saber 11°.",
            },
            {
                "tipo": "infografia",
                "titulo": "Infografía Saber 11° - Prueba Lectura Crítica",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": (
                    "Infografía oficial descargable al final de la sección, con competencias y "
                    "tipos de texto de la prueba de Lectura Crítica."
                ),
            },
            {
                "tipo": "guia_orientacion",
                "titulo": "Guía de orientación examen Saber 11°",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/guia-de-orientacion-examen-saber-11/",
                "descripcion": (
                    "Guía oficial que describe la estructura del examen, número de preguntas y "
                    "ejemplos de ítems."
                ),
            },
        ],
    },

    "Matemáticas": {
        "codigo_area": "MAT",
        "descripcion": (
            "Evalúa las competencias para enfrentar situaciones que requieren el uso de "
            "herramientas matemáticas en las categorías de álgebra y cálculo, geometría y "
            "estadística."
        ),
        "competencias": [
            {
                "nombre": "Interpretación y representación",
                "descripcion": (
                    "Comprender, transformar y representar información, así como extraer la "
                    "información relevante en contextos diversos."
                ),
            },
            {
                "nombre": "Formulación y ejecución",
                "descripcion": (
                    "Plantear y ejecutar estrategias matemáticas para resolver problemas en "
                    "distintos contextos."
                ),
            },
            {
                "nombre": "Argumentación",
                "descripcion": (
                    "Validar o refutar conclusiones, soluciones, estrategias e interpretaciones "
                    "desde el razonamiento matemático."
                ),
            },
        ],
        "herramientas": {
            "genericas": (
                "Herramientas matemáticas necesarias para interactuar de manera crítica en la sociedad."
            ),
            "no_genericas": (
                "Herramientas específicas del quehacer matemático aprendidas en la etapa escolar."
            ),
        },
        "fuentes": [
            {
                "tipo": "pagina_oficial",
                "titulo": "Saber 11° - ICFES",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": "Página oficial general del examen Saber 11°.",
            },
            {
                "tipo": "infografia",
                "titulo": "Infografía Saber 11° - Prueba Matemáticas",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": (
                    "Infografía oficial descargable al final de la sección, con competencias y "
                    "enfoque de la prueba de Matemáticas."
                ),
            },
            {
                "tipo": "guia_orientacion",
                "titulo": "Guía de orientación examen Saber 11°",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/guia-de-orientacion-examen-saber-11/",
                "descripcion": "Guía de orientación oficial del examen Saber 11°.",
            },
        ],
    },

    "Ciencias Naturales": {
        "codigo_area": "CN",
        "descripcion": (
            "Evalúa la capacidad del estudiante para comprender y usar nociones, conceptos y "
            "teorías de las ciencias naturales en la solución de problemas, valorando de manera "
            "crítica el conocimiento científico y sus consecuencias en la sociedad y el ambiente."
        ),
        "competencias": [
            {
                "nombre": "Indagación",
                "descripcion": (
                    "Reconocer preguntas, procedimientos e información relevante; buscar, "
                    "seleccionar e interpretar datos científicos."
                ),
            },
            {
                "nombre": "Explicación de fenómenos",
                "descripcion": (
                    "Analizar críticamente argumentos, modelos y explicaciones sobre fenómenos "
                    "naturales."
                ),
            },
            {
                "nombre": "Uso comprensivo del conocimiento científico",
                "descripcion": (
                    "Emplear conceptos, teorías y modelos científicos para resolver problemas en "
                    "distintos contextos."
                ),
            },
        ],
        "componentes": [
            "Químico (cambios químicos, estructura de la materia, mezclas, gases, energía).",
            "Biológico (seres vivos, herencia, reproducción, relaciones ecológicas, evolución).",
            "Físico (movimiento, energía, ondas, electromagnetismo, gravitación).",
            "Ciencia, Tecnología y Sociedad (CTS) en contextos locales y globales.",
        ],
        "fuentes": [
            {
                "tipo": "pagina_oficial",
                "titulo": "Saber 11° - ICFES",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": "Página oficial general del examen Saber 11°.",
            },
            {
                "tipo": "infografia",
                "titulo": "Infografía Saber 11° - Prueba Ciencias Naturales",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": (
                    "Infografía oficial con competencias y componentes de la prueba de "
                    "Ciencias Naturales."
                ),
            },
            {
                "tipo": "guia_orientacion",
                "titulo": "Guía de orientación examen Saber 11°",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/guia-de-orientacion-examen-saber-11/",
                "descripcion": "Guía de orientación oficial del examen Saber 11°.",
            },
        ],
    },

    "Inglés": {
        "codigo_area": "ING",
        "descripcion": (
            "Evalúa la competencia comunicativa en lengua inglesa del estudiante, de acuerdo "
            "con el Marco Común Europeo, mediante tareas de lectura, gramática y léxico."
        ),
        "estructura": {
            "resumen": (
                "La prueba se organiza en siete partes, que incluyen emparejamiento de "
                "descripciones, interpretación de avisos, conversaciones cortas y textos con espacios."
            ),
            "partes": [
                "Parte 1: Emparejar descripciones con palabras (una de ejemplo, 5 correctas, 2 sobrantes).",
                "Parte 2: Relacionar avisos con los lugares o situaciones correspondientes.",
                "Parte 3: Completar conversaciones cortas escogiendo la respuesta correcta.",
                "Parte 4: Completar un texto con espacios, eligiendo la palabra que encaja en la estructura.",
                "Parte 5: Comprensión de lectura sobre un texto de nivel básico.",
                "Parte 6: Comprensión de lectura sobre un texto de mayor complejidad.",
                "Parte 7: Completar un texto con espacios eligiendo la palabra con significado y estructura correctos.",
            ],
        },
        "fuentes": [
            {
                "tipo": "pagina_oficial",
                "titulo": "Saber 11° - ICFES",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": "Página oficial general del examen Saber 11°.",
            },
            {
                "tipo": "infografia",
                "titulo": "Infografía Saber 11° - Prueba Inglés",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": (
                    "Infografía oficial con la descripción por partes de la prueba de Inglés."
                ),
            },
            {
                "tipo": "guia_orientacion",
                "titulo": "Guía de orientación examen Saber 11°",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/guia-de-orientacion-examen-saber-11/",
                "descripcion": "Guía de orientación oficial del examen Saber 11°.",
            },
        ],
    },

    "Sociales y Ciudadanas": {
        "codigo_area": "SOC",
        "descripcion": (
            "Evalúa los conocimientos y habilidades que permiten comprender el mundo social "
            "desde la perspectiva de las ciencias sociales y el ejercicio de la ciudadanía."
        ),
        "competencias": [
            {
                "nombre": "Pensamiento social",
                "descripcion": (
                    "Usar conceptos básicos de las ciencias sociales para comprender problemáticas "
                    "y fenómenos sociales, políticos, económicos, culturales y geográficos, así "
                    "como principios de la Constitución y del sistema político colombiano."
                ),
            },
            {
                "nombre": "Pensamiento reflexivo y sistémico",
                "descripcion": (
                    "Reconocer distintas formas de aproximarse a los problemas sociales, identificar "
                    "la complejidad de las relaciones que los conforman y adoptar posturas críticas."
                ),
            },
            {
                "nombre": "Interpretación y análisis de perspectivas",
                "descripcion": (
                    "Analizar problemas sociales desde las perspectivas de los actores involucrados "
                    "e interpretar fuentes y argumentos enmarcados en problemáticas sociales."
                ),
            },
        ],
        "fuentes": [
            {
                "tipo": "pagina_oficial",
                "titulo": "Saber 11° - ICFES",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": "Página oficial general del examen Saber 11°.",
            },
            {
                "tipo": "infografia",
                "titulo": "Infografía Saber 11° - Prueba Sociales y Ciudadanas",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/",
                "descripcion": (
                    "Infografía oficial con competencias y enfoque de la prueba de Sociales y Ciudadanas."
                ),
            },
            {
                "tipo": "guia_orientacion",
                "titulo": "Guía de orientación examen Saber 11°",
                "url": "https://www.icfes.gov.co/evaluaciones-icfes/saber-11/guia-de-orientacion-examen-saber-11/",
                "descripcion": "Guía de orientación oficial del examen Saber 11°.",
            },
        ],
    },
}

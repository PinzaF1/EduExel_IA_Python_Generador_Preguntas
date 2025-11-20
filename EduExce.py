# EduExcel.py — Generador de Preguntas ICFES con OpenAI (MODO RÍGIDO)
# ------------------------------------------------------------
# Generador de preguntas tipo ICFES usando OpenAI GPT
# - Genera preguntas en formato JSON
# - Soporta 5 áreas: Lenguaje, Matemáticas, Sociales, Ciencias, Inglés
# - 4 estilos de aprendizaje de Kolb
# - ÁREA INGLÉS: pregunta y opciones en INGLÉS, explicación en ESPAÑOL
# - Generación de packs: hasta 100 preguntas (máximo)
# - MODO RÍGIDO: Validaciones estrictas, sin fallbacks, sin tolerancia a errores
# - Compatible con: gpt-4o, gpt-5-pro, o1-preview, y otros modelos OpenAI
# - Endpoints: /icfes/catalogo, /icfes/validar, /icfes/generar, /icfes/generar_pack, /debug/raw,
#              /icfes/doc_justificacion
# ------------------------------------------------------------

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
import os
import json
import re
import random
import unicodedata
import time

# ===================== Documentación oficial ICFES (bloque para Confluence) =====================

ICFES_DOC_CONFLUENCE = """
# Documentación sobre el uso de información oficial del ICFES para la generación automática de preguntas tipo Saber 11 con IA

## 1. Objetivo del documento

El propósito de este documento es justificar el uso de la documentación oficial del ICFES sobre el examen Saber 11 en un sistema de generación automática de preguntas mediante Inteligencia Artificial. Además, se explica para qué se emplea dicha documentación dentro del flujo de trabajo del sistema, de modo que cualquier persona que revise el proyecto entienda que las preguntas generadas no son arbitrarias, sino que siguen los lineamientos formales del examen de Estado.

---

## 2. Contexto: examen Saber 11 y documentación oficial

El Examen de Estado de la Educación Media, Saber 11, es una prueba estandarizada que mide la calidad de la educación impartida a los estudiantes que culminan la educación media. Está compuesto por cinco pruebas:

* Lectura Crítica
* Matemáticas
* Ciencias Naturales
* Sociales y Ciudadanas
* Inglés

El ICFES publica para cada una de estas pruebas documentos e infografías oficiales donde se describen:

* Las competencias que se evalúan
* Los componentes o ejes temáticos principales
* El tipo de textos, problemas o situaciones que se utilizan
* La forma general de las preguntas y del cuadernillo

Esta información es la base para que cualquier instrumento de evaluación que pretenda asemejarse al Saber 11 mantenga coherencia con el examen real.

---

## 3. Por qué usamos la documentación oficial del ICFES

### 3.1 Alineación con los estándares de evaluación del país

La documentación oficial asegura que las preguntas generadas por la IA estén alineadas con los estándares establecidos por el ICFES. El examen Saber 11 es un referente nacional, por lo que sus especificaciones definen qué se considera una competencia básica en lectura, matemáticas, ciencias, sociales y lengua extranjera.

Incorporar esta información garantiza que:

* Se respete la manera en que el ICFES entiende cada competencia
* Las preguntas apunten a los mismos objetivos del examen real
* Los resultados obtenidos con el sistema sean comparables en enfoque con los del Saber 11

---

### 3.2 Rigor conceptual y disciplinar

Cada prueba se define en términos de competencias, procesos cognitivos y componentes temáticos. La IA requiere estas definiciones para generar preguntas válidas, evitando ejercicios superficiales o descontextualizados.

El uso de documentación oficial permite:

* Diferenciar entre ejercicios de memoria y ejercicios que realmente evalúan análisis y comprensión
* Mantener el vocabulario técnico adecuado
* Adaptarse al nivel esperado para estudiantes de grado 11

---

### 3.3 Coherencia en la estructura de las preguntas

El formato del Saber 11 utiliza preguntas de opción múltiple con distractores funcionales. Para replicar este estilo, la IA debe conocer:

* La forma del enunciado
* Los tipos de distractores que usa el examen
* El tipo de textos, problemas o gráficos que se incluyen

El uso de la documentación oficial previene:

* Preguntas ambiguas
* Opciones poco realistas
* Ítems que no coinciden con la lógica del examen

---

### 3.4 Control de dificultad y nivel cognitivo

Las pruebas Saber 11 evalúan comprender, aplicar, analizar y evaluar. La documentación del ICFES describe lo que se espera de cada nivel cognitivo.

A partir de esto, la IA puede:

* Ajustar la dificultad según la competencia
* Generar preguntas sencillas, intermedias y complejas
* Crear problemas que exigen razonamiento, no solo memoria

---

### 3.5 Calidad, confiabilidad y trazabilidad

Utilizar fuentes oficiales permite rastrear cada pregunta hasta su fundamento conceptual. Esto facilita:

* Auditar el banco de preguntas
* Verificar que cada ítem se ajusta a su competencia correspondiente
* Realizar mejoras o actualizaciones basadas en cambios del ICFES

---

## 4. Para qué usamos la documentación del ICFES en la IA

### 4.1 Definir plantillas y parámetros de generación

La IA utiliza la documentación oficial para estructurar correctamente:

* Competencias por prueba
* Componentes temáticos
* Tipos de textos o problemas
* Formatos válidos de enunciado

La IA no genera preguntas sin guía; se basa en estas plantillas formales.

---

### 4.2 Etiquetar cada pregunta con información pedagógica

Cada pregunta generada queda clasificada según:

* Área
* Competencia
* Componente
* Tipo de texto o situación

Esto permite filtrar, organizar o seleccionar preguntas según necesidades pedagógicas, utilizando el lenguaje oficial del ICFES.

---

### 4.3 Generar explicaciones coherentes de respuesta

La documentación oficial también se usa para generar explicaciones precisas. La IA explica cada respuesta basándose en:

* La competencia evaluada
* El proceso cognitivo
* El distractor que representa un error típico

Esto brinda retroalimentación útil y alineada con los lineamientos del examen.

---

### 4.4 Entrenar y ajustar modelos de IA

Las especificaciones del ICFES sirven como referencia para evaluar si el modelo está produciendo preguntas válidas. Gracias a esto es posible:

* Detectar desviaciones del modelo
* Ajustar la frecuencia de competencias
* Corregir sesgos o formulaciones incorrectas

---

### 4.5 Comunicación clara con docentes, estudiantes y directivos

Indicar que el sistema utiliza documentación oficial del ICFES transmite confianza y claridad sobre el propósito del generador:

* No reemplaza al examen real
* Está diseñado para práctica y preparación
* Usa terminología oficial y estructura alineada con el Saber 11

---

## 5. Conclusión

La utilización de documentación oficial del ICFES es fundamental para la generación automática de preguntas tipo Saber 11 mediante IA.

Gracias a estas fuentes:

* Las preguntas generadas respetan competencias, componentes y niveles cognitivos
* El banco de preguntas resulta confiable y coherente
* Se garantiza que el diseño de evaluaciones se mantenga alineado con estándares nacionales

El uso de estas especificaciones permite que el sistema sea riguroso, trazable, educativo y técnicamente sólido.
"""

# ===================== Configuración =====================
load_dotenv(find_dotenv(), override=True)

# Configuración OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o") 
STRICT_MODE = True  # Siempre en modo estricto - más rígido
DEBUG_JSON = os.getenv("DEBUG_JSON", "0") == "1"
SEED_RANDOMIZE = os.getenv("SEED_RANDOMIZE", "1") == "1"

# Validación estricta de API Key
if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
    raise ValueError("OPENAI_API_KEY es requerida y no puede estar vacía")

# Validación estricta del formato de API Key
if not OPENAI_API_KEY.startswith(("sk-", "sk-proj-")):
    raise ValueError("OPENAI_API_KEY debe comenzar con 'sk-' o 'sk-proj-'")

# Validación estricta del modelo
MODELOS_VALIDOS = [
    "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo",
    "gpt-5-pro", "gpt-5", "o1-preview", "o1-mini", "o3-mini"
]
if OPENAI_MODEL not in MODELOS_VALIDOS and not OPENAI_MODEL.startswith("gpt-"):
    raise ValueError(f"Modelo '{OPENAI_MODEL}' no reconocido. Modelos válidos: {', '.join(MODELOS_VALIDOS)}")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="EduExcel - Generador de Preguntas ICFES (Modo Rígido)",
    description=(
        "API para generar preguntas tipo ICFES con estilos de aprendizaje de Kolb. "
        "Modo rígido con validaciones estrictas. Las preguntas se alinean con la documentación oficial "
        "del examen Saber 11 del ICFES (competencias, componentes y niveles cognitivos)."
    ),
    version="2.0.0-rigido"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _dbg(msg: str):
    """Debug helper para imprimir mensajes si DEBUG_JSON está activado."""
    if DEBUG_JSON:
        print(str(msg)[:2000])

# ===================== Catálogo de Áreas, Subtemas y Estilos =====================
ALLOWED: Dict[str, List[str]] = {
    "sociales": [
        "Constitución de 1991 y organización del Estado",
        "Historia de Colombia - Frente Nacional",
        "Guerras Mundiales y Guerra Fría",
        "Geografía de Colombia (mapas, territorio y ambiente)",
    ],
    "Ciencias Naturales": [
        "Indagación científica (variables, control e interpretación de datos)",
        "Fuerzas, movimiento y energía",
        "Materia y cambios (mezclas, reacciones y conservación)",
        "Genética y herencia",
        "Ecosistemas y cambio climático (CTS)",
    ],
    "Inglés": [
        "Verb to be (am, is, are)",
        "Present Simple (afirmación, negación y preguntas)",
        "Past Simple (verbos regulares e irregulares)",
        "Comparatives and superlatives",
        "Subject/Object pronouns & Possessive adjectives",
    ],
    "Lenguaje": [
        "Comprensión lectora (sentido global y local)",
        "Conectores lógicos (causa, contraste, condición, secuencia)",
        "Identificación de argumentos y contraargumentos",
        "Idea principal y propósito comunicativo",
        "Hecho vs. opinión e inferencias",
    ],
    "Matemáticas": [
        "Operaciones con números enteros",
        "Razones y proporciones",
        "Regla de tres simple y compuesta",
        "Porcentajes y tasas (aumento, descuento, interés simple)",
        "Ecuaciones lineales y sistemas 2×2",
    ],
}

KOLB_STYLES = ["Convergente", "Asimilador", "Acomodador", "Divergente"]

# Guías de enunciado por subtema (exactas a tus nombres)
SUBTEMA_GUIDE = {
    "Matemáticas": {
        "Operaciones con números enteros":
            "Crea un mini-caso con saldo/temperatura en 2–3 eventos y varias operaciones encadenadas (evita signos + en positivos).",
        "Razones y proporciones":
            "Plantea mezcla/receta con proporción fija; incluye dos datos y pide el tercero (sin + en positivos).",
        "Regla de tres simple y compuesta":
            "Caso de obreros/tiempos o máquinas/producción; explícita si es directa o inversa (sin + en positivos).",
        "Porcentajes y tasas (aumento, descuento, interés simple)":
            "Precio inicial, descuento y un ajuste adicional (impuesto o recargo) para el total (sin + en positivos).",
        "Ecuaciones lineales y sistemas 2×2":
            "Dos ecuaciones con contexto y solución única; opciones como pares ordenados.",
    },
    "Lenguaje": {
        "Comprensión lectora (sentido global y local)":
            "Fragmento de 3–4 frases con datos y opiniones; pide sentido global sin confundir detalles.",
        "Conectores lógicos (causa, contraste, condición, secuencia)":
            "Incluye conectores variados; pregunta por el que mantiene la relación lógica.",
        "Identificación de argumentos y contraargumentos":
            "Incluye tesis, razones y contraargumento explícito; pide reconocerlos.",
        "Idea principal y propósito comunicativo":
            "Señala pistas de intención (informar/persuadir) y cierre; pide la síntesis central.",
        "Hecho vs. opinión e inferencias":
            "Combina datos verificables y juicios de valor; pide distinguir e inferir con evidencia.",
    },
    "sociales": {
        "Constitución de 1991 y organización del Estado":
            "Menciona funciones/órganos y derechos; pide finalidad/alcance.",
        "Historia de Colombia - Frente Nacional":
            "Contexto histórico (años, actores, objetivos) sin anacronismos; interpreta consecuencias.",
        "Guerras Mundiales y Guerra Fría":
            "Tensiones ideológicas y efectos geopolíticos; pregunta por el rasgo central.",
        "Geografía de Colombia (mapas, territorio y ambiente)":
            "Relieve/clima vs. asentamientos/actividades; elegir síntesis coherente.",
    },
    "Ciencias Naturales": {
        "Indagación científica (variables, control e interpretación de datos)":
            "Diseño experimental con VI/VD y dos controles; identificar correctamente.",
        "Fuerzas, movimiento y energía":
            "Caso con masa, fuerza y variación de velocidad; relacionar con la 2ª ley de Newton.",
        "Materia y cambios (mezclas, reacciones y conservación)":
            "Mezcla homogénea con separación por método físico; conservación de masa.",
        "Genética y herencia":
            "Cruce monohíbrido con dominancia completa; proporciones en F2.",
        "Ecosistemas y cambio climático (CTS)":
            "Cambio de uso del suelo y biodiversidad; conclusión basada en evidencia.",
    },
    "Inglés": {
        "Verb to be (am, is, are)":
            "Mini-diálogo con pistas de número/persona; forma correcta.",
        "Present Simple (afirmación, negación y preguntas)":
            "Rutinas diarias; terceras personas; -s y do/does.",
        "Past Simple (verbos regulares e irregulares)":
            "Adverbios de pasado; forma correcta irregular.",
        "Comparatives and superlatives":
            "Comparación de objetos concretos; cuidado con 'more/—er'.",
        "Subject/Object pronouns & Possessive adjectives":
            "Ambigüedad sujeto/objeto/posesivo; elige forma adecuada.",
    },
}

# ===================== Utilidades de Normalización =====================
def _norm(s: str) -> str:
    """Normaliza un string eliminando acentos y espacios extra."""
    s = (s or "").strip().lower().replace("×", "x")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s)
    return s

def _closest(x: str, opciones: List[str]) -> Tuple[str, float]:
    """Encuentra la opción más similar a x usando difflib."""
    import difflib
    matches = difflib.get_close_matches(x, opciones, n=1, cutoff=0.0)
    if not matches:
        return "", 0.0
    ratio = difflib.SequenceMatcher(None, x, matches[0]).ratio()
    return matches[0], ratio

# ===================== Validación =====================
def catalogo():
    """Retorna el catálogo completo de áreas, subtemas y estilos Kolb."""
    return {
        "areas": list(ALLOWED.keys()),
        "subtemas_por_area": ALLOWED,
        "estilos_kolb": KOLB_STYLES,
        "kolb_descripcion": {
            "Convergente": "Aplicación práctica y solución única, con datos explícitos y pasos claros.",
            "Asimilador": "Énfasis en conceptos, organización lógica y relaciones; más estructura conceptual.",
            "Acomodador": "Contexto experiencial y toma de decisiones; casos situados y realistas.",
            "Divergente": "Múltiples perspectivas y síntesis; escenario rico en matices pero con respuesta única.",
        },
    }

def validar_area(area: str) -> Tuple[Optional[str], Optional[str]]:
    """Valida y normaliza el nombre del área."""
    if area in ALLOWED:
        return area, None
    mapa = {_norm(k): k for k in ALLOWED.keys()}
    nn = _norm(area)
    if nn in mapa:
        return mapa[nn], None
    mejor, _ = _closest(area, list(ALLOWED.keys()))
    return None, f"Área no permitida: '{area}'. ¿Quisiste decir '{mejor}'?"

def validar_subtema(area: str, subtema: str) -> Tuple[Optional[str], Optional[str]]:
    """Valida y normaliza el nombre del subtema para un área."""
    if area not in ALLOWED:
        return None, f"Área inválida: '{area}'."
    lst = ALLOWED[area]
    if subtema in lst:
        return subtema, None
    mapa = {_norm(x): x for x in lst}
    nn = _norm(subtema)
    if nn in mapa:
        return mapa[nn], None
    mejor, _ = _closest(subtema, lst)
    return None, f"Subtema no permitido para {area}: '{subtema}'. Sugerencia: '{mejor}'."

def validar_kolb(estilo: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Valida y normaliza el estilo de aprendizaje de Kolb."""
    if not estilo:
        return "Convergente", None
    for k in KOLB_STYLES:
        if _norm(k) == _norm(estilo):
            return k, None
    mejor, _ = _closest(estilo, KOLB_STYLES)
    return None, f"Estilo Kolb no reconocido: '{estilo}'. Sugerencia: '{mejor}'."

# ===================== Modelos Pydantic =====================
class GenInput(BaseModel):
    """Modelo de entrada para generar preguntas con validaciones estrictas."""
    area: str = Field(..., min_length=3, max_length=50, description="Área de conocimiento")
    subtema: str = Field(..., min_length=5, max_length=200, description="Subtema específico")
    estilo_kolb: Optional[str] = Field(None, max_length=20, description="Estilo de aprendizaje de Kolb")
    longitud_min: int = Field(200, ge=50, le=500, description="Longitud mínima en palabras (ICFES: 200-350)")
    longitud_max: int = Field(350, ge=100, le=1000, description="Longitud máxima en palabras (ICFES: 200-350)")
    max_tokens_item: int = Field(600, ge=100, le=4000, description="Máximo de tokens por item")
    temperatura: float = Field(0.2, ge=0.0, le=2.0, description="Temperatura de generación (0-2)")
    
    @classmethod
    def validate_longitud(cls, v, values):
        """Valida que longitud_min < longitud_max"""
        if 'longitud_min' in values and v < values['longitud_min']:
            raise ValueError("longitud_max debe ser mayor que longitud_min")
        return v
    
    class Config:
        validate_assignment = True
        str_strip_whitespace = True

class ItemOut(BaseModel):
    """Modelo de salida para una pregunta generada con validaciones estrictas."""
    area: str = Field(..., min_length=3, max_length=50)
    subtema: str = Field(..., min_length=5, max_length=200)
    estilo_kolb: Optional[str] = Field(None, max_length=20)
    pregunta: str = Field(..., min_length=10, max_length=5000)
    opciones: Dict[str, str] = Field(..., min_items=4, max_items=4)
    respuesta_correcta: str = Field(..., pattern="^[ABCD]$")
    explicacion: str = Field("", min_length=0, max_length=2000)
    meta: Dict[str, object] = Field(default_factory=dict)
    
    @classmethod
    def validate_opciones(cls, v):
        """Valida que existan exactamente 4 opciones A, B, C, D"""
        if not isinstance(v, dict):
            raise ValueError("opciones debe ser un diccionario")
        required_keys = {"A", "B", "C", "D"}
        if set(v.keys()) != required_keys:
            raise ValueError(f"opciones debe contener exactamente A, B, C, D. Recibido: {list(v.keys())}")
        for key, value in v.items():
            if not isinstance(value, str) or len(value.strip()) < 1:
                raise ValueError(f"Opción {key} no puede estar vacía")
        return v
    
    class Config:
        validate_assignment = True
        str_strip_whitespace = True

# ===================== Parser y Normalización de JSON =====================
def ensure_schema(d: dict):
    """Valida estrictamente que el diccionario tenga la estructura correcta."""
    if not isinstance(d, dict):
        raise ValueError("Salida no es objeto JSON. Debe ser un diccionario.")
    
    # Validación estricta de campos requeridos
    campos_requeridos = ["pregunta", "opciones", "respuesta_correcta"]
    for k in campos_requeridos:
        if k not in d:
            raise ValueError(f"Campo requerido '{k}' faltante en la respuesta")
        if d[k] is None:
            raise ValueError(f"Campo '{k}' no puede ser None")
    
    # Validación estricta de pregunta
    if not isinstance(d["pregunta"], str):
        raise ValueError("'pregunta' debe ser una cadena de texto")
    if len(d["pregunta"].strip()) < 10:
        raise ValueError("'pregunta' debe tener al menos 10 caracteres")
    
    # Validación estricta de opciones
    if not isinstance(d["opciones"], dict):
        raise ValueError("'opciones' debe ser un objeto/diccionario")
    
    opciones_requeridas = {"A", "B", "C", "D"}
    opciones_recibidas = set(d["opciones"].keys())
    
    if opciones_recibidas != opciones_requeridas:
        faltantes = opciones_requeridas - opciones_recibidas
        extras = opciones_recibidas - opciones_requeridas
        error_msg = f"Opciones inválidas. "
        if faltantes:
            error_msg += f"Faltantes: {faltantes}. "
        if extras:
            error_msg += f"Extras no permitidas: {extras}."
        raise ValueError(error_msg)
    
    # Validación estricta de cada opción
    for k in opciones_requeridas:
        valor = d["opciones"][k]
        if not isinstance(valor, str):
            raise ValueError(f"Opción {k} debe ser una cadena de texto")
        if len(valor.strip()) < 1:
            raise ValueError(f"Opción {k} no puede estar vacía")
    
    # Validación estricta de respuesta_correcta
    respuesta = str(d["respuesta_correcta"]).strip().upper()
    if respuesta not in ("A", "B", "C", "D"):
        raise ValueError(f"respuesta_correcta inválida: '{d['respuesta_correcta']}'. Debe ser A, B, C o D")
    d["respuesta_correcta"] = respuesta
    
    # Validación de explicación
    if "explicacion" not in d or d["explicacion"] is None:
        d["explicacion"] = ""
    elif not isinstance(d["explicacion"], str):
        raise ValueError("'explicacion' debe ser una cadena de texto")
    
    # Validación estricta de meta
    meta = d.get("meta", {})
    if not isinstance(meta, dict):
        raise ValueError("'meta' debe ser un objeto/diccionario")
    d["meta"] = meta

def parse_json_min(text: str) -> dict:
    """Parsea JSON desde el texto del modelo con validación estricta."""
    if not text or not isinstance(text, str):
        raise ValueError("Salida vacía o inválida del modelo. Se esperaba un string JSON.")
    
    # Limpieza inicial
    s = text.strip()
    
    # Eliminar markdown code blocks si existen
    if "```json" in s:
        s = re.sub(r"```json\s*", "", s)
    if "```" in s:
        s = re.sub(r"```\s*", "", s)
    
    # Normalizar comillas (nota: este bloque asume caracteres estándar en la práctica)
    s = s.replace("“", '"').replace("”", '"')
    s = s.strip()
    
    # Validación estricta: debe empezar y terminar con llaves
    if not s.startswith("{"):
        raise ValueError("El JSON debe empezar con '{'. Posible texto adicional antes del JSON.")
    if not s.endswith("}"):
        raise ValueError("El JSON debe terminar con '}'. Posible texto adicional después del JSON.")
    
    # Intentar parsear JSON directo
    try:
        parsed = json.loads(s)
        if not isinstance(parsed, dict):
            raise ValueError("El JSON debe ser un objeto, no un array u otro tipo")
        return parsed
    except json.JSONDecodeError as e:
        # Intentar extraer JSON si hay texto adicional
        m = re.search(r"\{.*\}", s, flags=re.S)
        if not m:
            raise ValueError(f"No se detectó JSON válido en la respuesta. Error: {str(e)}")
        blob = m.group(0)
        # Intentar arreglar trailing commas
        blob = re.sub(r",\s*([}\]])", r"\1", blob)
        try:
            parsed = json.loads(blob)
            if not isinstance(parsed, dict):
                raise ValueError("El JSON extraído debe ser un objeto")
            return parsed
        except json.JSONDecodeError as e2:
            raise ValueError(f"JSON inválido incluso después de limpieza. Error: {str(e2)}")

def coerce_single_item(obj: dict) -> dict:
    """Extrae un solo item si viene dentro de un array 'items'."""
    if isinstance(obj, dict) and "items" in obj and isinstance(obj["items"], list) and obj["items"] and isinstance(obj["items"][0], dict):
        obj = obj["items"][0]
    return obj

def normalize_keys_es(d: dict) -> dict:
    """Normaliza las claves del JSON a español, aceptando variaciones."""
    if not isinstance(d, dict):
        return d
    # Pregunta
    for k in ["pregunta", "enunciado", "statement", "prompt", "stem", "question", "texto", "planteamiento"]:
        if k in d:
            d["pregunta"] = d.pop(k)
            break
    # Opciones
    if "opciones" not in d:
        for k in ["opciones", "alternativas", "choices", "options", "respuestas"]:
            if k in d:
                val = d.pop(k)
                if isinstance(val, dict):
                    d["opciones"] = {
                        "A": val.get("A") or val.get("a") or val.get("1") or val.get("option_a") or "",
                        "B": val.get("B") or val.get("b") or val.get("2") or val.get("option_b") or "",
                        "C": val.get("C") or val.get("c") or val.get("3") or val.get("option_c") or "",
                        "D": val.get("D") or val.get("d") or val.get("4") or val.get("option_d") or "",
                    }
                elif isinstance(val, list):
                    labs = ["A", "B", "C", "D"]
                    d["opciones"] = {labs[i]: (val[i] if i < len(val) else "") for i in range(4)}
                else:
                    d["opciones"] = {"A": "", "B": "", "C": "", "D": ""}
                break
    # Respuesta correcta
    if "respuesta_correcta" not in d:
        for k in ["respuesta_correcta", "respuesta", "correcta", "answer", "ans", "correct_option", "correct", "solucion", "solution"]:
            if k in d:
                ans_raw = str(d.pop(k)).strip().upper()
                if ans_raw in ["1", "2", "3", "4"]:
                    ans_raw = {"1": "A", "2": "B", "3": "C", "4": "D"}[ans_raw]
                if ans_raw not in ["A", "B", "C", "D"]:
                    low = ans_raw.lower()
                    if "a" in low:
                        ans_raw = "A"
                    elif "b" in low:
                        ans_raw = "B"
                    elif "c" in low:
                        ans_raw = "C"
                    elif "d" in low:
                        ans_raw = "D"
                d["respuesta_correcta"] = re.sub(r"[^ABCD]", "", ans_raw) or "A"
                break
    d.setdefault("explicacion", "")
    meta = d.get("meta", {})
    if not isinstance(meta, dict):
        meta = {}
    d["meta"] = meta
    return d

# ===================== Procesamiento de Texto =====================
def _word_count(s: str) -> int:
    """Cuenta el número de palabras en un string."""
    return len(re.findall(r"\w+", s or "", flags=re.UNICODE))

def pad_to_range(texto: str, min_palabras: int, max_palabras: int) -> str:
    """Ajusta el texto a un rango de palabras."""
    extras = [
        "Lee cuidadosamente los indicios antes de decidir",
        "Contrasta propósito, procedimientos y evidencias del caso",
        "Evita confundir ejemplos con definiciones generales",
        "Verifica coherencia entre datos y conclusión elegida",
        "Selecciona la alternativa que mejor sintetiza la idea central"
    ]
    texto = (texto or "").strip()
    w, k = _word_count(texto), 0
    while w < min_palabras and k < len(extras):
        if texto and not texto.endswith((".", "?", "!", "…")):
            texto += ". "
        texto += extras[k]
        k += 1
        w = _word_count(texto)
    if w > max_palabras:
        sents = re.split(r"(?<=[.!?])\s+", texto)
        nuevo, cnt = [], 0
        for s in sents:
            sw = _word_count(s)
            if cnt + sw <= max_palabras:
                nuevo.append(s)
                cnt += sw
            else:
                break
        texto = " ".join(nuevo).strip()
    return texto

def remove_plus_on_positive(text: str) -> str:
    """Elimina signos + delante de números positivos."""
    def repl(m):
        num = m.group(2)
        return m.group(1) + num
    pattern = re.compile(r'(^|[^0-9\-\.,])\+(\d+(?:[.,]\d+)?)')
    return pattern.sub(repl, text)

def clean_options_signs(opciones: Dict[str, str]) -> Dict[str, str]:
    """Limpia signos + de todas las opciones."""
    out = {}
    for k, v in opciones.items():
        if isinstance(v, str):
            out[k] = remove_plus_on_positive(v)
        else:
            out[k] = v
    return out

def shuffle_options(opciones: dict, correcta_label: str) -> Tuple[dict, str]:
    """Baraja las opciones y ajusta la respuesta correcta."""
    labels = ["A", "B", "C", "D"]
    pairs = [(k, opciones.get(k, "").strip()) for k in labels]
    if len(set(v for _, v in pairs)) < 4:
        return opciones, correcta_label
    random.shuffle(pairs)
    new_op, new_label = {}, None
    for i, (old_label, text) in enumerate(pairs):
        lab = labels[i]
        new_op[lab] = text
        if old_label == correcta_label:
            new_label = lab
    return new_op, (new_label or correcta_label)

# ===================== Generación de Explicaciones =====================
def build_explanation_per_area(area: str, correcta: str) -> str:
    """Genera explicación por área. Todas en ESPAÑOL (incluso para Inglés)."""
    if "matem" in _norm(area):
        base = [
            f"Correcta ({correcta}).",
            "A: Aplica correctamente las operaciones requeridas.",
            "B: Presenta error de signos u orden de operaciones.",
            "C: Confunde la relación de proporcionalidad o el cálculo intermedio.",
            "D: Conclusión que no se deduce del enunciado."
        ]
    elif "lenguaj" in _norm(area):
        base = [
            f"Correcta ({correcta}).",
            "A: Resume la idea central con soporte textual.",
            "B: Confunde un detalle local con la tesis del texto.",
            "C: Generaliza más allá de la evidencia.",
            "D: Atribuye una intención no respaldada."
        ]
    elif "sociales" in _norm(area):
        base = [
            f"Correcta ({correcta}).",
            "A: Sintetiza finalidad/alcance con coherencia histórica.",
            "B: Confunde propósito con procedimiento o episodio aislado.",
            "C: Reduce el análisis a un caso puntual sin generalidad.",
            "D: Contradice la evidencia del proceso descrito."
        ]
    elif "ciencias" in _norm(area):
        base = [
            f"Correcta ({correcta}).",
            "A: Identifica variables y controles coherentes con el método.",
            "B: Intercambia VI y VD o ignora controles.",
            "C: Toma un control como variable principal.",
            "D: Conclusión no sustentada por el diseño."
        ]
    elif "ingl" in _norm(area):  # Inglés: explicación en ESPAÑOL
        base = [
            f"Correcta ({correcta}).",
            "A: Respeta la regla gramatical objetivo (forma/concordancia).",
            "B: Error de concordancia sujeto–verbo o uso incorrecto del tiempo verbal.",
            "C: Tiempo verbal incorrecto o forma no válida según el contexto.",
            "D: Pronombre/posesivo mal seleccionado o estructura gramatical incorrecta."
        ]
    else:
        base = [
            f"Correcta ({correcta}).",
            "A: Respeta la regla objetivo (forma/concordancia).",
            "B: Error de concordancia sujeto–verbo.",
            "C: Tiempo verbal incorrecto o forma no válida.",
            "D: Pronombre/posesivo mal seleccionado."
        ]
    return " ".join(base)

def fix_explanation_coherence(explicacion: str, correcta: str, area: str) -> str:
    """Asegura coherencia de la explicación y que esté en español para Inglés."""
    # Para área de Inglés, asegurar que la explicación esté en español
    if "ingl" in _norm(area):
        if isinstance(explicacion, str) and len(explicacion) > 0:
            # Detectar si está mayormente en inglés (heurística simple)
            palabras_comunes_es = ["correcta", "porque", "debido", "explicación", "opción", "respuesta"]
            palabras_comunes_en = ["correct", "because", "due", "explanation", "option", "answer"]
            explicacion_lower = explicacion.lower()
            count_es = sum(1 for p in palabras_comunes_es if p in explicacion_lower)
            count_en = sum(1 for p in palabras_comunes_en if p in explicacion_lower)
            
            if count_en > count_es:
                # Parece estar en inglés, usar plantilla en español
                return build_explanation_per_area(area, correcta)
    
    if not isinstance(explicacion, str):
        return build_explanation_per_area(area, correcta)
    patt = re.compile(r"(correcta\s*\(?\s*([ABCD])\s*\)?|la\s+respuesta\s+correcta\s+es\s+([ABCD]))", re.I)
    m = patt.search(explicacion)
    if m:
        return build_explanation_per_area(area, correcta)
    if len(explicacion.strip()) < 12:
        return build_explanation_per_area(area, correcta)
    if not re.search(rf"\b{re.escape(correcta)}\b", explicacion):
        encabezado = f"Correcta ({correcta}). "
        return encabezado + explicacion.strip()
    return explicacion

# ===================== Prompts para OpenAI =====================
def system_prompt(area: str = None) -> str:
    """Genera el prompt del sistema según el área."""
    base = (
        "Eres un generador experto de ÍTEMS tipo ICFES para el examen Saber 11. "
        "Todas las preguntas deben estar alineadas con la documentación oficial del ICFES: "
        "competencias, componentes temáticos y niveles cognitivos (comprender, aplicar, analizar, evaluar). "
        "DEVUELVES EXCLUSIVAMENTE JSON VÁLIDO (sin Markdown ni texto fuera del JSON). "
        "Esquema por ítem: {\"area\":\"\",\"subtema\":\"\",\"estilo_kolb\":\"\",\"pregunta\":\"\","
        "\"opciones\":{\"A\":\"\",\"B\":\"\",\"C\":\"\",\"D\":\"\"},\"respuesta_correcta\":\"\",\"explicacion\":\"\",\"meta\":{}} "
        "Para varias preguntas: {\"items\":[OBJ1,...,OBJN]}. "
        "LONG_MIN..LONG_MAX palabras, 4 opciones A–D y única correcta, "
        "explicación breve y coherente con 'respuesta_correcta'. "
        "No contradigas la 'respuesta_correcta' en la explicación; si detectas inconsistencia, ajusta la explicación."
    )
    
    # Si es área de Inglés, instrucciones especiales
    if area and "ingl" in _norm(area):
        return base + (
            "\n\nREGLAS ESPECIALES PARA ÁREA INGLÉS: "
            "- La PREGUNTA debe estar COMPLETAMENTE en INGLÉS. "
            "- Las OPCIONES (A, B, C, D) deben estar COMPLETAMENTE en INGLÉS. "
            "- La EXPLICACIÓN debe estar COMPLETAMENTE en ESPAÑOL, explicando por qué la respuesta es correcta y por qué las otras son incorrectas."
        )
    else:
        return base + " Reglas: Todo en ESPAÑOL (pregunta, opciones y explicación)."

def user_prompt(cfg):
    """Genera el prompt del usuario con la configuración específica."""
    estilo = cfg.estilo_kolb or "Convergente"
    guide = SUBTEMA_GUIDE.get(cfg.area, {}).get(cfg.subtema, "Incluye un mini-caso realista de 2–3 frases.")
    sociales_note = ""
    if "sociales" in _norm(cfg.area):
        sociales_note = (
            " Evita anacronismos y atribuciones erróneas de actores/fechas. "
            "No confundas 'Frente Nacional' con procesos posteriores; conserva coherencia histórica."
        )
    mates_note = ""
    if "matem" in _norm(cfg.area):
        mates_note = " No uses el signo '+' delante de enteros positivos en enunciado u opciones."
    
    # Nota especial para Inglés
    ingles_note = ""
    if "ingl" in _norm(cfg.area):
        ingles_note = (
            " IMPORTANTE: La pregunta y TODAS las opciones (A, B, C, D) deben estar en INGLÉS. "
            "La explicación debe estar en ESPAÑOL, explicando por qué la opción correcta es la adecuada y por qué las otras son incorrectas."
        )
    
    return (
        f"Genera UNA pregunta del área {cfg.area}, subtema EXACTO {cfg.subtema}. "
        f"Estilo Kolb: {estilo}. "
        f"Usa este enfoque: {guide}{sociales_note}{mates_note}{ingles_note} "
        "Alinea la competencia, el componente temático y el nivel cognitivo con las especificaciones oficiales del examen Saber 11 del ICFES. "
        f"IMPORTANTE: La pregunta debe tener entre {cfg.longitud_min} y {cfg.longitud_max} palabras (longitud típica de ICFES). "
        "Texto extenso con contexto completo; evita preguntas cortas o de una sola frase. "
        f"LONG_MIN {cfg.longitud_min} palabras, LONG_MAX {cfg.longitud_max} palabras. "
        "Devuelve SOLO el JSON del esquema indicado; sin texto adicional. "
        "Varía números, nombres y contexto; evita repetir patrones."
    )

# ===================== Integración con OpenAI =====================
def chat_openai(messages: List[dict], max_tokens: int, temperature: float) -> Tuple[str, Dict[str, int]]:
    """
    Llama a la API de OpenAI Chat Completions con validación estricta.
    messages: [{'role':'system'|'user'|'assistant', 'content':'...'}, ...]
    Devuelve una tupla: (contenido JSON como string, información de uso de tokens)
    """
    # Validación estricta de parámetros
    if not isinstance(messages, list) or len(messages) == 0:
        raise ValueError("messages debe ser una lista no vacía")
    
    for msg in messages:
        if not isinstance(msg, dict):
            raise ValueError("Cada mensaje debe ser un diccionario")
        if "role" not in msg or "content" not in msg:
            raise ValueError("Cada mensaje debe tener 'role' y 'content'")
        if msg["role"] not in ("system", "user", "assistant"):
            raise ValueError(f"Role inválido: {msg['role']}. Debe ser system, user o assistant")
    
    if not isinstance(max_tokens, int) or max_tokens < 1:
        raise ValueError(f"max_tokens debe ser un entero positivo. Recibido: {max_tokens}")
    
    if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
        raise ValueError(f"temperature debe estar entre 0 y 2. Recibido: {temperature}")
    
    seed_val = random.randint(1, 10_000_000) if SEED_RANDOMIZE else 42
    
    try:
        # Configuración para modelos que soportan JSON mode
        kwargs = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }
        
        # Algunos modelos (como o1-preview) no soportan response_format
        # GPT-5 PRO y modelos recientes deberían soportarlo
        if OPENAI_MODEL not in ["o1-preview", "o1-mini", "o3-mini"]:
            kwargs["response_format"] = {"type": "json_object"}
        
        # Seed solo para modelos que lo soportan (si no randomizamos)
        if OPENAI_MODEL not in ["o1-preview", "o1-mini", "o3-mini"] and not SEED_RANDOMIZE:
            kwargs["seed"] = seed_val
        
        response = client.chat.completions.create(**kwargs)
        
        if not response or not response.choices:
            raise ValueError("Respuesta vacía de OpenAI API")
        
        if len(response.choices) == 0:
            raise ValueError("No hay choices en la respuesta de OpenAI")
        
        content = response.choices[0].message.content
        
        if not content or not isinstance(content, str):
            raise ValueError("Contenido de respuesta vacío o inválido")
        
        if len(content.strip()) == 0:
            raise ValueError("Contenido de respuesta está vacío")
        
        # Extraer información de uso de tokens
        usage_info = {
            "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
            "completion_tokens": response.usage.completion_tokens if response.usage else 0,
            "total_tokens": response.usage.total_tokens if response.usage else 0
        }
        
        _dbg(f"RAW(JSON)>> modelo={OPENAI_MODEL} seed={seed_val} tokens={usage_info['total_tokens']} :: " + content[:1000])
        return content.strip(), usage_info
        
    except Exception as e:
        error_msg = f"Error en OpenAI API (modelo: {OPENAI_MODEL}): {str(e)}"
        _dbg(error_msg)
        raise Exception(error_msg)

# ===================== Validación de Entrada =====================
def validar_input(cfg: 'GenInput') -> Tuple['GenInput', List[str]]:
    """Valida y normaliza todos los parámetros de entrada con validación estricta."""
    errores = []
    
    # Validación estricta de área
    area_ok = None
    if not cfg.area or not isinstance(cfg.area, str):
        errores.append("El área es requerida y debe ser una cadena de texto")
    else:
        area_ok, err = validar_area(cfg.area.strip())
        if err:
            errores.append(err)
            area_ok = None
    
    # Validación estricta de subtema (solo si área es válida)
    sub_ok = None
    if area_ok:
        if not cfg.subtema or not isinstance(cfg.subtema, str):
            errores.append("El subtema es requerido y debe ser una cadena de texto")
        else:
            sub_ok, err2 = validar_subtema(area_ok, cfg.subtema.strip())
            if err2:
                errores.append(err2)
                sub_ok = None
    else:
        if not errores:
            errores.append("Primero corrige el área antes de validar el subtema")
    
    # Validación estricta de estilo Kolb
    kolb_ok, err3 = validar_kolb(cfg.estilo_kolb)
    if err3:
        errores.append(err3)
    
    # Validación estricta de rangos
    if cfg.longitud_min >= cfg.longitud_max:
        errores.append(f"longitud_min ({cfg.longitud_min}) debe ser menor que longitud_max ({cfg.longitud_max})")
    
    if cfg.max_tokens_item < 100:
        errores.append(f"max_tokens_item ({cfg.max_tokens_item}) debe ser al menos 100")
    
    if cfg.temperatura < 0 or cfg.temperatura > 2:
        errores.append(f"temperatura ({cfg.temperatura}) debe estar entre 0 y 2")
    
    if errores:
        return cfg, errores
    
    # Crear configuración validada
    cfg2 = GenInput(
        area=area_ok,
        subtema=sub_ok,
        estilo_kolb=kolb_ok,
        longitud_min=cfg.longitud_min,
        longitud_max=cfg.longitud_max,
        max_tokens_item=cfg.max_tokens_item,
        temperatura=cfg.temperatura,
    )
    return cfg2, []

# ===================== Generación de Preguntas =====================
def generar_una(cfg: 'GenInput') -> Tuple['ItemOut', Dict[str, int]]:
    """
    Genera una pregunta usando OpenAI.
    Retorna una tupla: (ItemOut, información de tokens usados)
    """
    msgs = [
        {"role": "system", "content": system_prompt(cfg.area)},
        {"role": "user", "content": user_prompt(cfg)},
    ]
    raw, usage1 = chat_openai(msgs, max_tokens=cfg.max_tokens_item, temperature=cfg.temperatura)
    total_tokens = usage1["total_tokens"]

    if "{" not in raw or "pregunta" not in raw:
        msgs.append({"role": "user", "content":
            "RECUERDA: devuelve SOLO UN OBJETO JSON EXACTO del esquema indicado. "
            "No escribas nada fuera del JSON. No uses 'items'. Incluye la clave 'pregunta'."})
        raw, usage2 = chat_openai(msgs, max_tokens=cfg.max_tokens_item, temperature=0.0)
        total_tokens += usage2["total_tokens"]
        usage1 = {
            "prompt_tokens": usage1["prompt_tokens"] + usage2["prompt_tokens"],
            "completion_tokens": usage1["completion_tokens"] + usage2["completion_tokens"],
            "total_tokens": total_tokens
        }

    data = parse_json_min(raw)
    data = coerce_single_item(data)
    data = normalize_keys_es(data)
    ensure_schema(data)

    # Post-procesamiento
    data["pregunta"] = pad_to_range(data.get("pregunta", ""), cfg.longitud_min, cfg.longitud_max)
    data["pregunta"] = remove_plus_on_positive(data["pregunta"])
    data["opciones"] = clean_options_signs(data.get("opciones", {}))

    op = data.get("opciones", {})
    rc = data.get("respuesta_correcta", "A")
    op2, rc2 = shuffle_options(op, rc)
    data["opciones"] = op2
    data["respuesta_correcta"] = rc2
    data["explicacion"] = fix_explanation_coherence(data.get("explicacion", ""), rc2, cfg.area)

    data["area"] = cfg.area
    data["subtema"] = cfg.subtema
    data["estilo_kolb"] = cfg.estilo_kolb or "Convergente"

    meta = data.get("meta", {})
    if not isinstance(meta, dict):
        meta = {}
    meta.setdefault("modelo", OPENAI_MODEL)
    meta.setdefault("seed_randomize", SEED_RANDOMIZE)
    # Agregar información de tokens usados
    meta.setdefault("tokens_usados", usage1)
    data["meta"] = meta

    return ItemOut(**data), usage1

def fallback_rule_based(cfg: 'GenInput') -> 'ItemOut':
    """Genera una pregunta de fallback si falla la generación con AI."""
    pregunta = (
        "Un caso práctico presenta datos y condiciones para analizar la relación central del problema. "
        "Evita sesgos de interpretación y valora la evidencia disponible antes de decidir."
    )
    opciones = {
        "A": "Conclusión coherente con la relación pedida.",
        "B": "Error por focalizar un detalle local.",
        "C": "Generalización sin soporte.",
        "D": "Afirmación no derivada de la evidencia."
    }
    correcta = "A"
    pregunta = pad_to_range(pregunta, cfg.longitud_min, cfg.longitud_max)
    opciones, correcta = shuffle_options(opciones, correcta)
    explicacion = build_explanation_per_area(cfg.area, correcta)
    return ItemOut(
        area=cfg.area,
        subtema=cfg.subtema,
        estilo_kolb=cfg.estilo_kolb or "Convergente",
        pregunta=pregunta,
        opciones=opciones,
        respuesta_correcta=correcta,
        explicacion=explicacion,
        meta={"source": "fallback", "modelo": OPENAI_MODEL}
    )

# ===================== Endpoints FastAPI =====================
@app.get("/")
def root():
    """Endpoint raíz con información de la API."""
    return {
        "nombre": "EduExcel - Generador de Preguntas ICFES",
        "version": "1.0.0",
        "modelo": OPENAI_MODEL,
        "endpoints": {
            "catalogo": "/icfes/catalogo",
            "validar": "/icfes/validar",
            "generar": "/icfes/generar",
            "generar_pack": "/icfes/generar_pack",
            "debug": "/debug/raw",
            "doc_justificacion": "/icfes/doc_justificacion"
        }
    }

@app.get("/icfes/catalogo")
def icfes_catalogo():
    """Lista las 5 áreas, sus subtemas y estilos Kolb con descripciones."""
    return {"ok": True, "catalogo": catalogo()}

@app.get("/icfes/doc_justificacion")
def icfes_doc_justificacion():
    """
    Devuelve la documentación interna (en formato Markdown/Confluence)
    que justifica el uso de la información oficial del ICFES para la
    generación automática de preguntas tipo Saber 11 con IA.
    """
    return {
        "ok": True,
        "formato": "markdown_confluence",
        "documentacion": ICFES_DOC_CONFLUENCE,
    }

@app.post("/icfes/validar")
def icfes_validar(cfg: GenInput):
    """Verifica SOLO la validez de área/subtema/estilo, sin generar preguntas."""
    cfg2, errores = validar_input(cfg)
    if errores:
        return {"ok": False, "errores": errores, "sugerencias": catalogo()}
    return {"ok": True, "normalizado": cfg2.model_dump(), "mensaje": "Parámetros válidos."}

@app.post("/icfes/generar")
def icfes_generar(cfg: GenInput):
    """Genera 1 ítem con validación estricta. No hay fallback en modo rígido."""
    cfg2, errores = validar_input(cfg)
    if errores:
        return {"ok": False, "generadas": 0, "resultados": [], "errores": [{"index": 0, "aviso": e} for e in errores]}
    try:
        item, tokens_info = generar_una(cfg2)
        # Validación estricta de la salida
        item_dict = item.model_dump()
        if not item_dict.get("pregunta") or len(item_dict["pregunta"]) < 10:
            raise ValueError("Pregunta generada no cumple con el mínimo de caracteres")
        if not all(k in item_dict.get("opciones", {}) for k in ["A", "B", "C", "D"]):
            raise ValueError("Faltan opciones en la respuesta generada")
        return {
            "ok": True,
            "generadas": 1,
            "resultados": [item_dict],
            "errores": [],
            "tokens": {
                "prompt_tokens": tokens_info["prompt_tokens"],
                "completion_tokens": tokens_info["completion_tokens"],
                "total_tokens": tokens_info["total_tokens"]
            }
        }
    except Exception as e:
        # En modo rígido, NO hay fallback - siempre se retorna error
        return {"ok": False, "generadas": 0, "resultados": [], "errores": [{"index": 0, "aviso": str(e)}]}

@app.post("/icfes/generar_pack")
def icfes_generar_pack(cfg: GenInput, cantidad: int = Query(5, ge=1, le=100, description="Cantidad de preguntas a generar (1-100)")):
    """Genera N ítems (hasta 100) con validación estricta. Sin fallback en modo rígido."""
    cfg2, errores = validar_input(cfg)
    if errores:
        return {"ok": False, "generadas": 0, "resultados": [], "errores": [{"index": 0, "aviso": e} for e in errores]}
    
    # Validación estricta de cantidad
    if not isinstance(cantidad, int) or cantidad < 1 or cantidad > 100:
        return {"ok": False, "generadas": 0, "resultados": [], "errores": [{"index": 0, "aviso": "cantidad debe estar entre 1 y 100"}]}
    
    resultados, errs, vistos = [], [], set()
    max_reintentos = 2  # Máximo 2 reintentos por pregunta en modo rígido
    
    # Contadores de tokens totales
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_tokens = 0
    
    for i in range(cantidad):
        intentos = 0
        generado = False
        
        while intentos < max_reintentos and not generado:
            try:
                it, tokens_info = generar_una(cfg2)
                it_dict = it.model_dump()
                
                # Acumular tokens usados
                total_prompt_tokens += tokens_info["prompt_tokens"]
                total_completion_tokens += tokens_info["completion_tokens"]
                total_tokens += tokens_info["total_tokens"]
                
                # Validación estricta de cada pregunta generada
                if not it_dict.get("pregunta") or len(it_dict["pregunta"]) < 10:
                    raise ValueError("Pregunta generada no cumple con el mínimo de caracteres")
                
                if not all(k in it_dict.get("opciones", {}) for k in ["A", "B", "C", "D"]):
                    raise ValueError("Faltan opciones en la respuesta generada")
                
                # Verificar duplicados
                if it_dict["pregunta"] in vistos:
                    if intentos < max_reintentos - 1:
                        time.sleep(0.1)
                        intentos += 1
                        continue
                    else:
                        raise ValueError("No se pudo generar pregunta única después de múltiples intentos")
                
                vistos.add(it_dict["pregunta"])
                resultados.append(it_dict)
                generado = True
                
            except Exception as e:
                intentos += 1
                if intentos >= max_reintentos:
                    errs.append({"index": i, "aviso": str(e), "intentos": intentos})
                    # En modo rígido, no continuamos con fallback
    
    # En modo rígido, solo retornamos OK si NO hay errores
    ok = (len(errs) == 0 and len(resultados) == cantidad)
    return {
        "ok": ok,
        "solicitadas": cantidad,
        "generadas": len(resultados),
        "resultados": resultados,
        "errores": errs,
        "tokens": {
            "prompt_tokens": total_prompt_tokens,
            "completion_tokens": total_completion_tokens,
            "total_tokens": total_tokens,
            "promedio_por_pregunta": round(total_tokens / max(len(resultados), 1), 2)
        }
    }

@app.post("/debug/raw")
def debug_raw(cfg: GenInput):
    """Muestra salida RAW del modelo (para depurar formato). Valida/normaliza antes."""
    cfg2, errores = validar_input(cfg)
    if errores:
        return {"ok": False, "errores": errores}
    msgs = [
        {"role": "system", "content": system_prompt(cfg2.area)},
        {"role": "user", "content": user_prompt(cfg2)},
    ]
    raw1, tokens1 = chat_openai(msgs, max_tokens=cfg2.max_tokens_item, temperature=cfg2.temperatura)
    if "{" not in raw1 or "pregunta" not in raw1:
        msgs.append({"role": "user", "content":
            "RECUERDA: devuelve SOLO UN OBJETO JSON EXACTO del esquema indicado. "
            "No escribas nada fuera del JSON. No uses 'items'. Incluye la clave 'pregunta'."})
        raw2, tokens2 = chat_openai(msgs, max_tokens=cfg2.max_tokens_item, temperature=0.0)
        return {
            "ok": True,
            "raw1": raw1,
            "raw2": raw2,
            "tokens1": tokens1,
            "tokens2": tokens2,
            "tokens_total": {
                "prompt_tokens": tokens1["prompt_tokens"] + tokens2["prompt_tokens"],
                "completion_tokens": tokens1["completion_tokens"] + tokens2["completion_tokens"],
                "total_tokens": tokens1["total_tokens"] + tokens2["total_tokens"]
            }
        }
    return {"ok": True, "raw": raw1, "tokens": tokens1}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

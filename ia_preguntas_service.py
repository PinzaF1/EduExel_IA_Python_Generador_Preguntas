import os
import json
import time
from typing import Any, Dict, List, Optional, TypedDict

from openai import OpenAI
from dotenv import load_dotenv

from icfes_saber11_fuentes import ICFES_AREA_ALIAS, ICFES_SABER11_FUENTES

load_dotenv()

# ============================================================
# TIPOS
# ============================================================

class PreguntaGenerada(TypedDict):
    pregunta: str
    opciones: Dict[str, str]  # { "A": "texto", "B": "texto", ... }
    respuesta_correcta: str
    explicacion: str


class RespuestaOpenAI(TypedDict):
    preguntas: List[PreguntaGenerada]


class PreguntaTransformada(TypedDict):
    orden: int
    pregunta: str
    opciones: Dict[str, str]         # Objeto original para guardar en JSON (BD)
    opcionesArray: List[str]         # Array formateado para enviar al móvil
    respuesta_correcta: str
    explicacion: str
    area: str
    subtema: str
    estilo_kolb: str


# ============================================================
# SERVICIO
# ============================================================

class IaPreguntasService:
    """
    Servicio para generar preguntas tipo ICFES Saber 11° usando OpenAI
    y el contexto oficial definido en icfes_saber11_fuentes.py
    """

    def __init__(self) -> None:
        self.enabled: bool = False
        self.client: Optional[OpenAI] = None
        self.model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout_ms: int = int(os.getenv("OPENAI_TIMEOUT_MS", "20000"))

        api_key = os.getenv("OPENAI_API_KEY", "")

        if not api_key:
            print("⚠️ [IA Preguntas] OPENAI_API_KEY no configurada - usando fallback a banco local")
            return

        self.client = OpenAI(
            api_key=api_key,
            base_url=os.getenv("OPENAI_BASE_URL") or None,
        )
        self.enabled = True

        print("✅ [IA Preguntas] SDK de OpenAI inicializado correctamente")
        print(f"   - Modelo: {self.model}")
        print(f"   - Timeout: {self.timeout_ms}ms")

    # --------------------------------------------------------

    def is_enabled(self) -> bool:
        """Verifica si el servicio está habilitado (si hay API key)."""
        return self.enabled

    # --------------------------------------------------------

    def generar_preguntas(
        self,
        area: str,
        subtema: str,
        estilo_kolb: str,
        cantidad: int,
    ) -> List[PreguntaTransformada]:
        """
        Genera preguntas tipo ICFES usando OpenAI y devuelve una lista
        de PreguntaTransformada listas para BD / móvil.
        """

        if not self.enabled or self.client is None:
            raise RuntimeError("Servicio de IA no habilitado - API key no configurada")

        print("🤖 [IA Preguntas] ═══════════════════════════════════════")
        print("[IA Preguntas] Generando preguntas con OpenAI SDK (Python):")
        print("   - Área:", area)
        print("   - Subtema:", subtema)
        print("   - Estilo Kolb:", estilo_kolb)
        print("   - Cantidad:", cantidad)
        print("   - Modelo:", self.model)
        print("   - Timeout:", self.timeout_ms, "ms")
        print("═══════════════════════════════════════════════════════════")

        system_prompt = self._construir_system_prompt(estilo_kolb, area)
        user_prompt = self._construir_user_prompt(area, subtema, cantidad)

        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0.2,  # Baja temperatura para respuestas más consistentes
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                timeout=self.timeout_ms / 1000.0,  # segundos
            )

            duration_ms = int((time.time() - start_time) * 1000)

            print("═══════════════════════════════════════════════════════════")
            print(f"✅ [IA Preguntas] Respuesta recibida en {duration_ms}ms")
            print("═══════════════════════════════════════════════════════════")

            content = response.choices[0].message.content
            if not content:
                raise ValueError("OpenAI no devolvió contenido")

            parsed: RespuestaOpenAI = json.loads(content)

            if not isinstance(parsed.get("preguntas"), list) or len(parsed["preguntas"]) == 0:
                raise ValueError("OpenAI no devolvió preguntas válidas")

            print(f"✅ [IA Preguntas] Parseadas {len(parsed['preguntas'])} preguntas correctamente")

            preguntas_transformadas: List[PreguntaTransformada] = []
            for index, pregunta in enumerate(parsed["preguntas"], start=1):
                preguntas_transformadas.append(
                    self._transformar_pregunta(
                        pregunta,
                        orden=index,
                        area=area,
                        subtema=subtema,
                        estilo_kolb=estilo_kolb,
                    )
                )

            print("═══════════════════════════════════════════════════════════")
            print(f"✅ [IA Preguntas] ÉXITO: {len(preguntas_transformadas)} preguntas generadas")
            print("═══════════════════════════════════════════════════════════")

            return preguntas_transformadas

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            print("❌ [IA Preguntas] ═══════════════════════════════════════")
            print("[IA Preguntas] 🚨 ERROR al generar preguntas")
            print(f"[IA Preguntas] Tiempo transcurrido: {duration_ms}ms")
            print(f"[IA Preguntas] TIPO: {type(e).__name__}")
            print(f"[IA Preguntas] MENSAJE: {e}")
            print("═══════════════════════════════════════════════════════════")
            raise

    # --------------------------------------------------------
    # PROMPTS
    # --------------------------------------------------------

    def _construir_system_prompt(self, estilo_kolb: str, area: str) -> str:
        caracteristicas_estilo: Dict[str, str] = {
            "Divergente": (
                "Enfócate en situaciones problema que requieran pensamiento creativo, "
                "análisis desde múltiples perspectivas y reflexión. Usa contextos cotidianos "
                "y preguntas abiertas que inviten a imaginar soluciones."
            ),
            "Asimilador": (
                "Prioriza la comprensión de teorías, modelos conceptuales y relaciones lógicas "
                "entre ideas. Incluye definiciones claras, explicaciones sistemáticas y preguntas "
                "que requieran razonamiento abstracto."
            ),
            "Convergente": (
                "Presenta problemas con una solución práctica y concreta. Enfócate en aplicación "
                "directa de conocimientos, resolución eficiente de problemas y preguntas con "
                "respuesta única y definida."
            ),
            "Acomodador": (
                "Usa escenarios reales, experimentación práctica y situaciones que requieran tomar "
                "decisiones rápidas. Incluye contextos dinámicos donde se aprende haciendo y "
                "ajustando sobre la marcha."
            ),
        }

        area_oficial = ICFES_AREA_ALIAS.get(area, area)
        info_area = ICFES_SABER11_FUENTES.get(area_oficial)
        contexto_area = ""

        if info_area:
            contexto_area += f'\n\nINFORMACIÓN OFICIAL DEL ÁREA "{area_oficial}" SEGÚN ICFES SABER 11°:\n'
            contexto_area += f"- Código de área: {info_area.get('codigo_area')}\n"
            contexto_area += f"- Descripción general: {info_area.get('descripcion')}\n"

            competencias = info_area.get("competencias") or []
            if competencias:
                contexto_area += "\nCOMPETENCIAS PRINCIPALES QUE DEBEN EVALUARSE:\n"
                for c in competencias:
                    contexto_area += f"- {c.get('nombre')}: {c.get('descripcion')}\n"

            componentes = info_area.get("componentes") or []
            if componentes:
                contexto_area += "\nCOMPONENTES CLAVE DEL ÁREA:\n"
                for comp in componentes:
                    contexto_area += f"- {comp}\n"

            tipos_textos = info_area.get("tipos_textos") or {}
            continuos = tipos_textos.get("continuos") or []
            discontinuos = tipos_textos.get("discontinuos") or []
            if continuos or discontinuos:
                contexto_area += "\nTIPOS DE TEXTOS QUE PUEDEN APARECER EN LAS PREGUNTAS:\n"
                if continuos:
                    contexto_area += "- Textos continuos:\n"
                    for t in continuos:
                        contexto_area += f"  * {t}\n"
                if discontinuos:
                    contexto_area += "- Textos discontinuos:\n"
                    for t in discontinuos:
                        contexto_area += f"  * {t}\n"

            herramientas = info_area.get("herramientas") or {}
            if herramientas:
                contexto_area += "\nHERRAMIENTAS MATEMÁTICAS A CONSIDERAR:\n"
                if herramientas.get("genericas"):
                    contexto_area += f"- Herramientas genéricas: {herramientas['genericas']}\n"
                if herramientas.get("no_genericas"):
                    contexto_area += f"- Herramientas no genéricas: {herramientas['no_genericas']}\n"

            estructura = info_area.get("estructura") or {}
            if estructura:
                contexto_area += "\nESTRUCTURA TÍPICA DE LA PRUEBA EN ESTA ÁREA:\n"
                if estructura.get("resumen"):
                    contexto_area += f"- Resumen: {estructura['resumen']}\n"
                partes = estructura.get("partes") or []
                if partes:
                    contexto_area += "- Partes:\n"
                    for p in partes:
                        contexto_area += f"  * {p}\n"

            fuentes = info_area.get("fuentes") or []
            if fuentes:
                contexto_area += (
                    "\nFUENTES OFICIALES DE REFERENCIA (ÚSALAS SOLO COMO CONTEXTO, "
                    "NO LAS MENCIONES EN LOS ENUNCIADOS):\n"
                )
                for f in fuentes:
                    contexto_area += (
                        f"- {f.get('titulo')} ({f.get('url')}): "
                        f"{f.get('descripcion')}\n"
                    )

        base_prompt = f"""Eres un experto generador de preguntas tipo ICFES (examen de estado colombiano) para estudiantes de grado 11.

CONTEXTO EDUCATIVO COLOMBIANO:
El ICFES (Instituto Colombiano para la Evaluación de la Educación) evalúa competencias en 5 áreas fundamentales.
Debes generar preguntas que evalúen competencias, no solo memorización.

ÁREAS Y SUBTEMAS OFICIALES:

📐 MATEMÁTICAS:
  - Operaciones con números enteros
  - Razones y proporciones
  - Regla de tres simple y compuesta
  - Porcentajes y tasas (aumento, descuento, interés simple)
  - Ecuaciones lineales y sistemas 2×2

📚 LENGUAJE (LECTURA CRÍTICA):
  - Comprensión lectora (sentido global y local)
  - Conectores lógicos (causa, contraste, condición, secuencia)
  - Identificación de argumentos y contraargumentos
  - Idea principal y propósito comunicativo
  - Hecho vs. opinión e inferencias

🌍 SOCIALES Y CIUDADANAS:
  - Constitución de 1991 y organización del Estado
  - Historia de Colombia - Frente Nacional
  - Guerras Mundiales y Guerra Fría
  - Geografía de Colombia (mapas, territorio y ambiente)

🔬 CIENCIAS NATURALES:
  - Indagación científica (variables, control e interpretación de datos)
  - Fuerzas, movimiento y energía
  - Materia y cambios (mezclas, reacciones y conservación)
  - Genética y herencia
  - Ecosistemas y cambio climático (CTS)

🌐 INGLÉS:
  - Verb to be (am, is, are)
  - Present Simple (afirmación, negación y preguntas)
  - Past Simple (verbos regulares e irregulares)
  - Comparatives and superlatives
  - Subject/Object pronouns & Possessive adjectives

ESTILO DE APRENDIZAJE KOLB: {estilo_kolb}
{caracteristicas_estilo.get(estilo_kolb, "")}

CARACTERÍSTICAS DE LAS PREGUNTAS:
- Nivel: Educación media (grado 10-11)
- Formato: Pregunta tipo ICFES (opción múltiple con única respuesta)
- Opciones: Exactamente 4 opciones (A, B, C, D)
- Longitud: 200-350 caracteres por pregunta
- Distracción: Las opciones incorrectas deben ser plausibles pero claramente erróneas
- Explicación: Breve justificación de por qué la respuesta es correcta
- Contexto colombiano: Usa nombres, lugares y situaciones relevantes para Colombia

FORMATO DE RESPUESTA (JSON estricto):
{{
  "preguntas": [
    {{
      "pregunta": "Texto de la pregunta aquí",
      "opciones": {{
        "A": "Primera opción",
        "B": "Segunda opción",
        "C": "Tercera opción",
        "D": "Cuarta opción"
      }},
      "respuesta_correcta": "A",
      "explicacion": "Breve explicación de por qué A es correcta"
    }}
  ]
}}

IMPORTANTE:
- Devuelve SOLO JSON válido, sin texto adicional
- Todas las preguntas deben estar en español
- respuesta_correcta debe ser exactamente "A", "B", "C" o "D"
- Cada pregunta debe ser única y relevante al área/subtema solicitado
- Usa el subtema EXACTO que se te solicita (respétalo literalmente)"""

        return base_prompt + contexto_area

    # --------------------------------------------------------

    def _construir_user_prompt(
        self,
        area: str,
        subtema: str,
        cantidad: int,
    ) -> str:
        area_oficial = ICFES_AREA_ALIAS.get(area, area)

        return f"""Genera {cantidad} preguntas tipo ICFES sobre:

Área interna (app): {area}
Área oficial ICFES Saber 11°: {area_oficial}
Subtema específico: {subtema}

Recuerda:
- {cantidad} preguntas diferentes
- Todas sobre el subtema: "{subtema}"
- Nivel de grado 11 (educación media colombiana)
- Formato JSON como especificado
- Adapta el enfoque según el estilo de aprendizaje Kolb indicado
- Asegúrate de que cada pregunta sea coherente con la descripción, competencias y estructura oficial del área "{area_oficial}" proporcionadas en el contexto del sistema.
"""

    # --------------------------------------------------------
    # TRANSFORMACIONES
    # --------------------------------------------------------

    def _transformar_pregunta(
        self,
        pregunta: PreguntaGenerada,
        orden: int,
        area: str,
        subtema: str,
        estilo_kolb: str,
    ) -> PreguntaTransformada:
        opciones_array = self._transformar_opciones(pregunta["opciones"])

        return {
            "orden": orden,
            "pregunta": pregunta["pregunta"],
            "opciones": pregunta["opciones"],
            "opcionesArray": opciones_array,
            "respuesta_correcta": pregunta["respuesta_correcta"].upper(),
            "explicacion": pregunta.get("explicacion", ""),
            "area": area,
            "subtema": subtema,
            "estilo_kolb": estilo_kolb,
        }

    # --------------------------------------------------------

    def _transformar_opciones(self, opciones: Dict[str, str]) -> List[str]:
        """
        Transforma opciones:
        Input:  { "A": "texto A", "B": "texto B", ... }
        Output: ["A. texto A", "B. texto B", ...]
        """
        return [
            f"{letra}. {texto}"
            for letra, texto in sorted(opciones.items(), key=lambda x: x[0])
        ]

    # --------------------------------------------------------
    # SALIDAS PARA BD / MÓVIL
    # --------------------------------------------------------

    def preparar_para_jsonb(
        self, preguntas: List[PreguntaTransformada]
    ) -> List[Dict[str, Any]]:
        """
        Prepara preguntas para guardar en BD (JSONB).
        """
        resultado: List[Dict[str, Any]] = []
        for p in preguntas:
            resultado.append(
                {
                    "orden": p["orden"],
                    "pregunta": p["pregunta"],
                    "opciones": p["opciones"],
                    "respuesta_correcta": p["respuesta_correcta"],
                    "explicacion": p["explicacion"],
                    "area": p["area"],
                    "subtema": p["subtema"],
                    "estilo_kolb": p["estilo_kolb"],
                }
            )
        return resultado

    def preparar_para_movil(
        self, preguntas: List[PreguntaTransformada]
    ) -> List[Dict[str, Any]]:
        """
        Prepara preguntas para enviar al móvil (sin respuestas correctas).
        """
        resultado: List[Dict[str, Any]] = []
        for p in preguntas:
            resultado.append(
                {
                    "id_pregunta": None,  # Las preguntas de IA no tienen id en BD
                    "area": p["area"],
                    "subtema": p["subtema"],
                    "enunciado": p["pregunta"],
                    "opciones": p["opcionesArray"],
                }
            )
        return resultado


# ============================================================
# PEQUEÑA PRUEBA MANUAL (opcional)
# ============================================================

if __name__ == "__main__":
    service = IaPreguntasService()

    if not service.is_enabled():
        print("Servicio no habilitado. Configura OPENAI_API_KEY en tu entorno.")
    else:
        preguntas = service.generar_preguntas(
            area="Matemáticas",
            subtema="Porcentajes y tasas",
            estilo_kolb="Convergente",
            cantidad=2,
        )

        print("\n--- Preguntas transformadas ---")
        print(json.dumps(preguntas, indent=2, ensure_ascii=False))

        print("\n--- Para JSONB ---")
        print(json.dumps(service.preparar_para_jsonb(preguntas), indent=2, ensure_ascii=False))

        print("\n--- Para móvil ---")
        print(json.dumps(service.preparar_para_movil(preguntas), indent=2, ensure_ascii=False))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core import load_strategies, render_strategy
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Pedagogy Radar API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LearningObjective(BaseModel):
    text: str
    taxonomy: str

class ScaffoldRequest(BaseModel):
    carrera: str = ""
    semestre: str = ""
    materia: str = ""
    tema: str = ""
    strategy_id: str
    activity_title: str
    activity_description: str
    learning_objectives: list[LearningObjective]
    prework_instructions: str = ""
    in_class_activity: str = ""

class SuggestRubricRequest(BaseModel):
    activity_title: str
    activity_description: str
    objectives: list[str]

class SuggestRubricResponse(BaseModel):
    rubric: str

class ScaffoldResponse(BaseModel):
    markdown: str

class EvidenceAlignmentRequest(BaseModel):
    objectives: list[str]
    activities: list[str]
    evidences: list[str]

class EvidenceAlignmentResponse(BaseModel):
    suggested_evidences: list[str]
    reasoning: str

class PreworkResource(BaseModel):
    title: str
    url: str
    type: str  # "paper", "video", "mooc", "podcast", "libro", etc.
    summary: str

class PreworkResourceResponse(BaseModel):
    resources: list[PreworkResource]

# -------- ENDPOINTS --------

@app.post("/scaffold", response_model=ScaffoldResponse)
def scaffold_activity(req: ScaffoldRequest):
    strategies = load_strategies()
    strategy = next((s for s in strategies if s.id == req.strategy_id), None)
    if not strategy:
        raise HTTPException(status_code=404, detail="Estrategia no encontrada.")

    context = req.dict()
    context.update({
        "expected_evidence": strategy.evidence,
        "implementation_notes": strategy.implementation_notes,
        "references": strategy.references,
    })
    markdown = render_strategy(strategy, context)
    return {"markdown": markdown}

@app.post("/suggest-objectives")
def suggest_objectives(req: ScaffoldRequest):
    try:
        from llm_utils import infer_objectives
        objs = infer_objectives(req, n=4)
        if not objs or (
            len(objs) == 1 and ("Redacta" in objs[0] or "objetivo" in objs[0].lower()) or len(objs[0]) < 25
        ):
            raise Exception("La API LLM no devolvió objetivos útiles.")
    except Exception as e:
        print("FALLBACK:", e)
        objs = [
            "Analizar conceptos clave del tema.",
            "Aplicar conocimientos en un caso práctico.",
            "Evaluar el impacto de la solución propuesta.",
            "Reflexionar sobre el proceso de aprendizaje."
        ]
    return {"objectives": objs}

@app.post("/suggest-activity")
def suggest_activity(req: ScaffoldRequest):
    try:
        from llm_utils import infer_activity
        activity = infer_activity(req)
        if not activity or "Redacta" in activity or len(activity) < 25:
            raise Exception("La IA no devolvió una actividad útil.")
    except Exception as e:
        print("FALLBACK actividad:", e)
        activity = (
            "Desarrollar una propuesta creativa aplicada al tema.\n"
            "Resolver ejercicios prácticos relacionados en grupo.\n"
            "Exponer resultados y reflexionar en clase."
        )
    return {"activity": activity}

@app.post("/suggest-rubric", response_model=SuggestRubricResponse)
def suggest_rubric(req: SuggestRubricRequest):
    # Puedes también recibir ScaffoldRequest completo si quieres más contexto
    prompt = (
        f"Genera una rúbrica de evaluación de 3 niveles para una actividad universitaria titulada '{req.activity_title}' "
        f"con esta descripción: '{req.activity_description}'. "
        f"Los objetivos de aprendizaje son: {', '.join(req.objectives)}.\n\n"
        "Sigue este formato:\n"
        "Nivel 1 (Aprueba): ...\n"
        "Nivel 2 (Destacado): ...\n"
        "Nivel 3 (Excelente): ...\n\n"
        "Sé claro, conciso y específico para cada nivel."
    )
    # El resto igual que antes...
    try:
        from transformers import pipeline
        pipe = pipeline("text-generation", model="google/flan-t5-small", trust_remote_code=True)
        outputs = pipe(prompt, max_new_tokens=180)
        raw = outputs[0]["generated_text"]
        if "Nivel 1" in raw:
            return {"rubric": raw}
    except Exception as e:
        print(f"[INFO] No se pudo usar modelo local para rúbrica: {e}")
    try:
        import os
        HF_API_TOKEN = os.getenv("HF_API_TOKEN")
        if HF_API_TOKEN:
            import requests
            api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 180}}
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            output = response.json()
            raw = output[0]["generated_text"] if isinstance(output, list) and "generated_text" in output[0] else output[0]
            if "Nivel 1" in raw:
                return {"rubric": raw}
    except Exception as e:
        print(f"[INFO] No se pudo usar HuggingFace API para rúbrica: {e}")
    try:
        import os
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY:
            import openai
            openai.api_key = OPENAI_API_KEY
            messages = [
                {"role": "system", "content": "Eres un experto en pedagogía universitaria."},
                {"role": "user", "content": prompt}
            ]
            chat_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=350,
                n=1,
                stop=None,
                temperature=0.3,
            )
            raw = chat_resp.choices[0].message.content
            if "Nivel 1" in raw:
                return {"rubric": raw}
    except Exception as e:
        print(f"[INFO] No se pudo usar OpenAI API para rúbrica: {e}")
    return {
        "rubric": (
            "Nivel 1 (Aprueba): Cumple parcialmente los objetivos. Identifica conceptos básicos, pero con poca profundidad.\n"
            "Nivel 2 (Destacado): Cumple todos los objetivos, analiza casos y aplica criterios de forma adecuada.\n"
            "Nivel 3 (Excelente): Supera los objetivos, propone ideas innovadoras y justifica sus decisiones con evidencia."
        )
    }

@app.post("/suggest-evidence-alignment", response_model=EvidenceAlignmentResponse)
def suggest_evidence_alignment(req: EvidenceAlignmentRequest):
    prompt = (
        f"Objetivos: {', '.join(req.objectives)}\n"
        f"Actividades: {', '.join(req.activities)}\n"
        f"Evidencias actuales: {', '.join(req.evidences)}\n"
        "Sugiere una lista alineada de evidencias de evaluación para cada objetivo, "
        "explica brevemente el porqué y si falta alguna evidencia importante."
    )
    # Aquí llamas a tu modelo local / HF / OpenAI, etc.
    # ... lógica igual que antes ...
    return {
        "suggested_evidences": [
            "Informe de caso",
            "Debate grupal",
            "Presentación grupal"
        ],
        "reasoning": (
            "El objetivo 'Analizar...' requiere análisis escrito (informe). "
            "La presentación valida la argumentación y el debate fomenta pensamiento crítico."
        )
    }

@app.post("/suggest-prework-resources", response_model=PreworkResourceResponse)
def suggest_prework_resources(req: ScaffoldRequest):
    # (Recomendado: en producción, primero intenta buscar recursos reales)
    try:
        from llm_utils import suggest_prework_resources
        resources = suggest_prework_resources(req, n=3)
        if not resources or len(resources) < 1:
            raise Exception("LLM no devolvió recursos útiles.")
    except Exception as e:
        print(f"[INFO] No se pudo sugerir recursos con LLM: {e}")
        resources = [
            {
                "title": "Content Marketing Strategies for SMEs: A Practical Guide",
                "url": "https://www.semanticscholar.org/paper/XXXXX",
                "type": "paper",
                "summary": "Paper con análisis de casos reales de marketing digital en pequeñas empresas."
            },
            {
                "title": "How Small Businesses Win with Content (YouTube)",
                "url": "https://www.youtube.com/watch?v=ZZZZZ",
                "type": "video",
                "summary": "Conferencia breve sobre tácticas efectivas para pymes en redes sociales."
            },
            {
                "title": "MOOC: Digital Marketing for Entrepreneurs (edX)",
                "url": "https://www.edx.org/course/digital-marketing-for-entrepreneurs",
                "type": "mooc",
                "summary": "Curso online gratis que cubre fundamentos de contenido digital."
            }
        ]
    # Mapea dicts a modelos BaseModel (si fuera necesario)
    resources = [PreworkResource(**r) if not isinstance(r, PreworkResource) else r for r in resources]
    return {"resources": resources}
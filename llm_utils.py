import os
import re


def query_llm(prompt, extract_fn, n=3):
    # 1. Local
    try:
        from transformers import pipeline
        MODEL_NAME = "google/flan-t5-small"
        pipe = pipeline("text-generation", model=MODEL_NAME, trust_remote_code=True)
        outputs = pipe(prompt, max_new_tokens=256)
        raw = outputs[0]["generated_text"]
        results = extract_fn(raw)
        if results:
            return results
    except Exception as e:
        print(f"[INFO] No se pudo usar modelo local: {e}")

    # 2. HuggingFace Inference API
    try:
        HF_API_TOKEN = os.getenv("HF_API_TOKEN")
        if HF_API_TOKEN:
            import requests
            api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
            headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
            payload = {"inputs": prompt, "parameters": {"max_new_tokens": 256}}
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            output = response.json()
            raw = output[0]["generated_text"] if isinstance(output, list) and "generated_text" in output[0] else output[0] if output else ""
            results = extract_fn(raw)
            if results:
                return results
    except Exception as e:
        print(f"[INFO] No se pudo usar HuggingFace API: {e}")

    # 3. OpenAI API
    try:
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if OPENAI_API_KEY:
            import openai
            openai.api_key = OPENAI_API_KEY
            messages = [
                {"role": "system", "content": "Eres un asistente pedagógico experto en educación superior."},
                {"role": "user", "content": prompt}
            ]
            chat_resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=500,
                n=1,
                stop=None,
                temperature=0.3,
            )
            raw = chat_resp.choices[0].message.content
            results = extract_fn(raw)
            if results:
                return results
    except Exception as e:
        print(f"[INFO] No se pudo usar OpenAI API: {e}")

    # 4. Fallback (puedes customizar según el caso de uso)
    return extract_fn("")  # O resultados hardcodeados si quieres

def build_context_prompt(data: dict) -> str:
    context = []
    if data.get("carrera"):
        context.append(f"Carrera: {data['carrera']}")
    if data.get("semestre"):
        context.append(f"Semestre: {data['semestre']}")
    if data.get("materia"):
        context.append(f"Materia o curso: {data['materia']}")
    if data.get("tema"):
        context.append(f"Tema de clase: {data['tema']}")
    return "\n".join(context)


def infer_objectives(req, n=4):
    data = req.dict() if hasattr(req, 'dict') else req
    context = build_context_prompt(data)
    prompt = (
        f"{context}\n\n"
        f"Redacta {n} objetivos de aprendizaje claros, observables y medibles para una actividad titulada '{data['activity_title']}' "
        f"con esta descripción: '{data['activity_description']}'. Usa frases cortas y verbos de la taxonomía de Bloom."
        "Devuélvelos como una lista numerada."
    )
    return query_llm(prompt, _extract_objectives, n)

def infer_activity(req, strategy_id=None):
    data = req.dict() if hasattr(req, 'dict') else req
    context = build_context_prompt(data)
    strategy = strategy_id or data.get("strategy_id", "")
    prompt = (
        f"{context}\n\n"
        f"Como experto en didáctica universitaria, diseña una actividad principal para la estrategia pedagógica '{strategy}'. "
        f"La actividad debe estar alineada con el título '{data['activity_title']}' y la descripción: '{data['activity_description']}'. "
        "Incluye pasos claros y concretos para estudiantes y docente, y especifica materiales si aplica."
    )
    # Para una sola actividad, retorna la primera de la lista
    result = query_llm(prompt, _extract_objectives, 1)
    return result[0] if result else ""

def suggest_prework_resources(req, n=3):
    data = req.dict() if hasattr(req, 'dict') else req
    context = build_context_prompt(data)
    prompt = (
        f"{context}\n\n"
        f"Sugiere {n} recursos de prework (artículos, videos, podcast, libros o cursos online) para una clase sobre '{data['activity_title']}'.\n"
        "Por cada recurso, incluye:\n"
        "- Título\n- Tipo (paper, video, curso, podcast, libro)\n- URL\n- Breve descripción (1 frase)\n"
        "Devuélvelos como una lista estructurada."
    )
    return query_llm(prompt, extract_resources, n)

def extract_resources(text):
    """
    Extrae recursos estructurados del output del LLM.
    Soporta outputs tipo markdown, lista numerada, o bloques.
    """
    resources = []
    # Busca líneas tipo "- [Título](url) [tipo]: desc"
    # O líneas separadas por atributos
    pattern = re.compile(
        r"-\s*(?P<title>.+?)\s*\[(?P<type>paper|video|curso|mooc|podcast|libro)\]\s*\((?P<url>https?://[^\s)]+)\)\s*[:-]\s*(?P<desc>.+)",
        re.IGNORECASE
    )
    for line in text.split('\n'):
        match = pattern.match(line)
        if match:
            resources.append({
                "title": match.group("title"),
                "type": match.group("type"),
                "url": match.group("url"),
                "description": match.group("desc")
            })
    # Fallback: busca por secciones básicas si no matchea nada
    if not resources:
        resources = [
            {"title": "Artículo ejemplo", "type": "paper", "url": "https://ejemplo.org", "description": "Un recurso de muestra."}
            for _ in range(3)
        ]
    return resources

def _extract_objectives(text):
    objectives = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Puede venir como "1. xxx" o "- xxx"
        if line[0].isdigit() and "." in line:
            obj = line.split(".", 1)[1].strip()
            objectives.append(obj)
        elif line.startswith("-") or line.startswith("•"):
            objectives.append(line[1:].strip())
    if not objectives and text:
        objectives = [l.strip("-• ") for l in text.split('\n') if l.strip()]
    return objectives
# pedagogy-radar

Pedagogical Strategy Radar for University Instructors  
Empower your classroom. Instantly transform any activity into multiple teaching strategies—powered by open-source LLMs. 

---

## 🚦 ¿Qué es pedagogy-radar?

**pedagogy-radar** es una herramienta open-source que permite a docentes universitarios adaptar cualquier actividad o brief a diferentes metodologías pedagógicas (PBL, flipped classroom, gamificación, aprendizaje colaborativo y más), alineadas con métricas clave (NSM) de su aula.

- Generador multiestrategia para actividades universitarias
- CLI y microservicio API para integración en servidores propios
- Catálogo editable de estrategias y NSM
- 100% privacidad, 100% open-source

---

## ✨ Características

- Scaffold automático de actividades en Markdown según metodología seleccionada
- Catálogo de estrategias y métricas customizables
- Plug-and-play: funciona en Linux, Windows, macOS (Docker-ready)
- Compatible con modelos LLM open-source (llama.cpp, GPT-J, etc.) Agrega tu API-KEY.
- Integración sencilla con plataformas educativas (Moodle, Canvas, etc.)
- Más de 10 estrategias pedagógicas integradas (editable vía YAML)  
- Generación de actividades listas para copiar/pegar en Notion, Obsidian o Word
- Compatible con LLMs locales, HuggingFace o OpenAI (opcional) 
- API FastAPI portable y multiusuario

---

## 🧠 Catálogo de Estrategias (inicio)
- Flipped classroom
- Aprendizaje basado en problemas (PBL)
- Gamificación
- Aprendizaje colaborativo
- Peer instruction
Revisar strategies.yaml
Contribuciones para nuevas estrategias ¡bienvenidas!

---


## 🛠️ Tech Stack

- Python 3.10+
- Typer (CLI)
- FastAPI (API)
- Jinja2 (templates)
- llama.cpp / transformers
- Docker (despliegue fácil)
- Next.js (opcional, frontend visualizador)

---

## 🚀 Uso inicial

```bash
# 1. Clona este repositorio
git clone https://github.com/ignacioplth/pedagogy-radar.git
cd pedagogy-radar

# 2. Instala dependencias
pip install -r requirements.txt

# 3. (Opcional) Añade tu clave de OpenAI o HuggingFace en .env
echo "OPENAI_API_KEY=sk-..." > .env

# 4. Ejecuta el servidor local
uvicorn api:app --reload
```

---

## ✨ ¿Cómo usarlo?
- Abre el generador en tu navegador: http://localhost:8000/docs
- Usa el endpoint /scaffold con los siguientes campos:
    - carrera, semestre, materia, tema
    - strategy_id (elige entre las estrategias disponibles)
    - activity_title, activity_description
    - learning_objectives: lista con campos text y taxonomy
    - prework_instructions, in_class_activity (opcional)
- Recibirás un bloque en Markdown con:
Actividad completa (preclase + clase)
    - Evidencia esperada
    - Sugerencias de implementación
    - Referencias pedagógicas
- ¡Copia y pega en tu diario digital docente! (Notion, Obsidian, HackMD, Word…)

---

## 📚 Diario pedagógico complementario

Este proyecto es 100% compatible con teacher-spark-book, un diario en Markdown para docentes que permite:
- Documentar cada clase
- Llevar bitácoras reflexivas
- Planificar próximos pasos

---

## 🧠 Ejemplo de estrategia

```bash
- id: flipped
  name: Clase Invertida (Flipped)
  template: flipped.md.jinja
  evidence: "Presentación grupal + resumen individual"
  implementation_notes: "Funciona muy bien en cursos con alto contenido teórico."
  references:
    - Bishop, J.L. & Verleger, M.A. (2013). The Flipped Classroom.
```

---

## 🧪 Ejemplo de output Markdown

```bash
## Actividad: Análisis de caso real con enfoque invertido

**Objetivos**:
- Analizar conceptos clave del marketing digital.
- Aplicar criterios de segmentación en un caso real.

**Preclase**:
- Ver video “Estrategias de contenido en PYMEs”
- Leer artículo: Content Marketing para no expertos

**En clase**:
- Discusión guiada en grupos
- Diseño de una mini campaña para un caso local

**Evidencia esperada**:
- Presentación en grupo
- Reflexión individual escrita

**Notas para implementación**:
Esta estrategia funciona mejor si se entregan los recursos al menos 48h antes de la clase.
```

---

## 🧪 Ejemplo de output Markdown

Puedes instalar esta API una vez en un servidor (local o nube) y compartir la misma instancia con hasta 30 docentes o más.
Cada docente puede pegar su salida en su propio diario o espacio personal.
No requiere base de datos ni autenticación para funcionar.

---

## 🧑‍🏫 ¿Para quién es esto?
- Docentes universitarios de cualquier disciplina
- Centros de innovación docente
- Universidades que quieran adoptar herramientas ligeras de IA
- Colectivos de pedagogía abierta

---

## 💡 Créditos
Proyecto iniciado por @ignacioplth

---

## 🪄 ¿Te gustaría contribuir?

¡Estás más que invitado!
Puedes proponer nuevas estrategias pedagógicas, mejorar plantillas, añadir soporte multilenguaje o colaborar en la interfaz visual.

---

## 🧭 Licencia

MIT — úsalo, compártelo y mejóralo.

---

## 📬 Contacto

¿Quieres integrar esto en tu universidad o colectivo docente?
Escríbeme: [ignacioplth \[at\] gmail.com](https://www.linkedin.com/in/andresquisbert/) o abre un issue en GitHub.

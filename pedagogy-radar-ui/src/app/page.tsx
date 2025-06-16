'use client';

import React, { useState, useRef, useEffect } from "react";
import { validarAlineacion } from "@/utils/bloomAlignment";
import ReactMarkdown from 'react-markdown';
import strategies from '../utils/strategies.json';


// Tipos
type ScaffoldReq = {
  carrera: string;
  semestre: string;
  materia: string;
  tema: string;
  strategy_id: string;
  activity_title: string;
  activity_description: string;
  learning_objectives: { text: string; taxonomy: string }[];
  prework_instructions: string;
  in_class_activity: string;
  evidences: string[];
  rubric: string;
};

type PreworkResource = {
  title: string;
  url: string;
  resource_type: string;
  summary: string;
};

type ObjectiveResp = { objectives: string[] };
type ActivityResp = { activity: string };
type RubricResp = { rubric: string };
type PreworkResourcesResp = { resources: PreworkResource[] };

export default function Home() {
  // States
  const [carrera, setCarrera] = useState("");
  const [semestre, setSemestre] = useState("");
  const [materia, setMateria] = useState("");
  const [tema, setTema] = useState("");
  const [strategyId, setStrategyId] = useState("flipped");
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [objectives, setObjectives] = useState("");
  const [prework, setPrework] = useState("");
  const [activity, setActivity] = useState("");
  const [evidences, setEvidences] = useState<string[]>(["Quiz", "Ensayo crítico"]);
  const [evidenceInput, setEvidenceInput] = useState("");
  const [markdown, setMarkdown] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestingObj, setSuggestingObj] = useState(false);
  const [suggestingAct, setSuggestingAct] = useState(false);
  const [error, setError] = useState("");
  const [warnings, setWarnings] = useState<string[]>([]);
  const [rubric, setRubric] = useState("");
  const [suggestingRubric, setSuggestingRubric] = useState(false);
  const [suggestingPrework, setSuggestingPrework] = useState(false);
  const [preworkResources, setPreworkResources] = useState<PreworkResource[]>([]);
  const [showPreworkSuggestions, setShowPreworkSuggestions] = useState(false);
  const [copied, setCopied] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const bloomLevels = [
    "Conocimiento", "Comprensión", "Aplicación", "Análisis", "Síntesis", "Evaluación"
  ];
  const [objectivesList, setObjectivesList] = useState<{text: string, taxonomy: string}[]>([]);
  const [showIntegrationHelp, setShowIntegrationHelp] = useState(false);

  // Real-time alignment validation
  useEffect(() => {
    setWarnings(
      validarAlineacion(
        objectives.split(";").map(x => x.trim()).filter(x => x.length > 0),
        [activity, ...evidences]
      )
    );
  }, [objectives, activity, evidences]);

  useEffect(() => {
    const arr = objectives.split(";").map(o => o.trim()).filter(o => o.length > 0);
    setObjectivesList(arr.map(obj => ({
      text: obj,
      taxonomy: "Conocimiento" // Default (puedes cambiar la lógica)
    })));
  }, [objectives]);

  // --- Util: request context (enviar siempre contexto completo para IA)
  function buildContextReq(): ScaffoldReq {
    return {
      carrera,
      semestre,
      materia,
      tema,
      strategy_id: strategyId,
      activity_title: title,
      activity_description: desc,
      learning_objectives: objectivesList.map(o => ({
        text: o.text,
        taxonomy: o.taxonomy
      })),
      prework_instructions: prework,
      in_class_activity: activity,
      evidences,
      rubric,
    };
  }

  // --- Fetches IA ---
  async function handleSuggestObjectives() {
    setSuggestingObj(true);
    setError("");
    try {
      const res = await fetch("http://127.0.0.1:8000/suggest-objectives", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildContextReq()),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: ObjectiveResp = await res.json();
      setObjectives(data.objectives.join("; "));
    } catch (err) {
      setError("Error sugiriendo objetivos con IA: " + (err as Error).message);
    } finally {
      setSuggestingObj(false);
    }
  }

  async function handleSuggestActivity() {
    setSuggestingAct(true);
    setError("");
    try {
      const res = await fetch("http://127.0.0.1:8000/suggest-activity", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildContextReq()),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: ActivityResp = await res.json();
      setActivity(data.activity);
    } catch (err) {
      setError("Error sugiriendo actividad con IA: " + (err as Error).message);
    } finally {
      setSuggestingAct(false);
    }
  }

  async function handleSuggestRubric() {
    setSuggestingRubric(true);
    setError("");
    try {
      const res = await fetch("http://127.0.0.1:8000/suggest-rubric", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildContextReq()),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: RubricResp = await res.json();
      setRubric(data.rubric);
    } catch (err) {
      setError("Error sugiriendo rúbrica con IA: " + (err as Error).message);
    } finally {
      setSuggestingRubric(false);
    }
  }

  async function handleSuggestPrework() {
    setSuggestingPrework(true);
    setShowPreworkSuggestions(true);
    setError("");
    try {
      const res = await fetch("http://127.0.0.1:8000/suggest-prework-resources", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildContextReq()),
      });
      if (!res.ok) throw new Error(await res.text());
      const data: PreworkResourcesResp = await res.json();
      setPreworkResources(data.resources);
    } catch (err) {
      setError("Error generando pre-work " + (err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  // --- Helpers ---
  function addPreworkResource(resource: PreworkResource) {
    const entry = `${resource.title} [${resource.resource_type}] ${resource.url}\n${resource.summary}`;
    setPrework(prework ? prework + "\n" + entry : entry);
    setShowPreworkSuggestions(false);
  }
  function clearPreworkSuggestions() {
    setPreworkResources([]);
    setShowPreworkSuggestions(false);
  }

  function copyMarkdown() {
    navigator.clipboard.writeText(markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  // Evidences: Multi-input/tag UX
  const evidenceInputRef = useRef<HTMLInputElement>(null);
  function handleEvidenceAdd(e: React.KeyboardEvent | React.MouseEvent) {
    e.preventDefault();
    if (
      evidenceInput.trim() &&
      !evidences.includes(evidenceInput.trim()) &&
      evidences.length < 6
    ) {
      setEvidences([...evidences, evidenceInput.trim()]);
      setEvidenceInput("");
      evidenceInputRef.current?.focus();
    }
  }
  function handleEvidenceRemove(idx: number) {
    setEvidences(evidences.filter((_, i) => i !== idx));
  }

  // --- Submit principal ---
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setMarkdown("");
    try {
      const res = await fetch("http://127.0.0.1:8000/scaffold", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildContextReq()),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setMarkdown(data.markdown);
    } catch (err) {
      setError("Error generando Markdown: " + (err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSuggestAlignment() {
    alert("Próximamente: Corrección de alineación con IA.");
  }

  // --- Render
  return (
    <main className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-6">Pedagogy Radar Copilot</h1>
      <form onSubmit={handleSubmit} className="space-y-4">

        {/* Contexto (opcional) */}
        <details className="border rounded p-3 mb-3 bg-gray-50" open>
          <summary className="text-sm text-gray-600 font-semibold cursor-pointer">
            Contexto de la actividad (opcional)
          </summary>
          <div className="mt-2">
            <label className="font-semibold">Carrera</label>
            <input className="w-full border rounded p-2 mb-2" value={carrera} onChange={e => setCarrera(e.target.value)} placeholder="Ej: Ingeniería Comercial"/>
            <div className="flex gap-2">
              <input className="flex-1 border rounded p-2" value={semestre} onChange={e => setSemestre(e.target.value)} placeholder="Semestre"/>
              <input className="flex-1 border rounded p-2" value={materia} onChange={e => setMateria(e.target.value)} placeholder="Materia/Curso"/>
            </div>
            <input className="w-full border rounded p-2 mt-2" value={tema} onChange={e => setTema(e.target.value)} placeholder="Tema de clase"/>
          </div>
        </details>

        {/* Estrategia */}
        <div>
          <label className="font-semibold">Estrategia</label>
          <select
            className="w-full border rounded p-2"
            value={strategyId}
            onChange={e => setStrategyId(e.target.value)}
          >
            {strategies.map(s => (
              <option key={s.id} value={s.id}>
                {s.display_name}
              </option>
            ))}
          </select>
        </div>
        {/* Título */}
        <div>
          <label className="font-semibold">Título</label>
          <input className="w-full border rounded p-2" value={title} onChange={e => setTitle(e.target.value)} required/>
        </div>
        {/* Descripción */}
        <div>
          <div className="flex items-center justify-between">
            <label className="font-semibold">Descripción</label>
            <span className="text-xs text-gray-400 ml-2">¿?</span>
          </div>
          <textarea
            className="w-full border rounded p-2"
            rows={2}
            value={desc}
            onChange={e => setDesc(e.target.value)}
            placeholder="Ej: Una empresa enfrenta caída de ventas y requiere una solución digital innovadora..."
            required
          />
        </div>
        {/* Objetivos */}
        <div>
          <div className="flex items-center justify-between">
            <label className="font-semibold">
              Objetivos de aprendizaje <span className="text-xs">(separa con ; )</span>
            </label>
            <button
              className="bg-purple-600 text-white px-4 py-2 rounded flex items-center gap-2"
              type="button"
              onClick={handleSuggestObjectives}
              disabled={suggestingObj || !title || !desc}
            >
              <span className="inline-block">⚡</span>
              {suggestingObj ? "Generando..." : "Construir con IA"}
            </button>
          </div>
          <textarea
            className="w-full border rounded p-2"
            rows={2}
            placeholder="Analizar campañas exitosas; Evaluar impacto en ventas"
            value={objectives}
            onChange={e => setObjectives(e.target.value)}
            required
          />
          {objectivesList.length > 0 && (
            <div className="mt-2 space-y-2">
              {objectivesList.map((obj, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <span className="text-sm">{obj.text}</span>
                  <select
                    value={obj.taxonomy}
                    className="border rounded p-1 text-xs"
                    onChange={e => {
                      const newList = [...objectivesList];
                      newList[idx].taxonomy = e.target.value;
                      setObjectivesList(newList);
                    }}
                  >
                    {bloomLevels.map(tax => <option key={tax} value={tax}>{tax}</option>)}
                  </select>
                </div>
              ))}
            </div>
          )}
        </div>
        {/* Prework */}
        <div>
          <div className="flex items-center justify-between">
            <label className="font-semibold">Instrucciones de prework</label>
            <button
              className="bg-purple-600 text-white px-4 py-2 rounded flex items-center gap-2"
              type="button"
              onClick={handleSuggestPrework}
              disabled={suggestingPrework || !title}
            >
              <span className="inline-block">⚡</span>
              {suggestingPrework ? "Generando..." : "Construir con IA"}
            </button>
          </div>
          <input className="w-full border rounded p-2" value={prework} onChange={e => setPrework(e.target.value)} placeholder="Ej: Leer artículo, ver video, hacer resumen..."/>
          {showPreworkSuggestions && preworkResources.length > 0 && (
            <div className="border rounded bg-gray-50 p-3 my-2">
              <div className="font-semibold mb-2">Recursos sugeridos:</div>
              <ul className="space-y-2">
                {preworkResources.map((res, i) => (
                  <li key={i} className="border rounded p-2 bg-white flex flex-col">
                    <a href={res.url} target="_blank" rel="noopener noreferrer" className="font-bold text-blue-700 hover:underline">{res.title}</a>
                    <div className="text-xs text-gray-700 mb-1">[{res.resource_type}] – {res.summary}</div>
                    <button
                      className="mt-1 text-xs bg-green-600 text-white px-2 py-1 rounded self-start"
                      onClick={() => addPreworkResource(res)}
                      type="button"
                    >Añadir al prework</button>
                  </li>
                ))}
              </ul>
              <button className="mt-2 text-xs bg-gray-300 text-gray-900 px-2 py-1 rounded" type="button" onClick={clearPreworkSuggestions}>Cerrar</button>
            </div>
          )}
        </div>
        {/* Actividad */}
        <div>
          <div className="flex items-center justify-between">
            <label className="font-semibold">Actividad en clase</label>
            <button
              className="bg-purple-600 text-white px-4 py-2 rounded flex items-center gap-2"
              type="button"
              onClick={handleSuggestActivity}
              disabled={suggestingAct || !title || !desc || !strategyId}
            >
              <span className="inline-block">⚡</span>
              {suggestingAct ? "Generando..." : "Construir con IA"}
            </button>
          </div>
          <input className="w-full border rounded p-2" value={activity} onChange={e => setActivity(e.target.value)} placeholder="Ej: Debate, resolución de ejercicios, presentación grupal..."/>
        </div>
        {/* Evidencias */}
        <div>
          <label className="font-semibold flex items-center gap-2">
            Evidencias esperadas
            <span className="text-xs text-gray-400 ml-1">?</span>
          </label>
          <div className="flex flex-wrap gap-2 mb-2">
            {evidences.map((ev, idx) => (
              <span key={idx} className="inline-flex items-center bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                {ev}
                <button className="ml-1 text-blue-600 hover:text-red-500" onClick={() => handleEvidenceRemove(idx)} title="Eliminar evidencia" type="button">×</button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              ref={evidenceInputRef}
              className="w-full border rounded p-2"
              value={evidenceInput}
              onChange={e => setEvidenceInput(e.target.value)}
              placeholder="Añadir evidencia y presiona Enter"
              onKeyDown={e => { if (e.key === "Enter") handleEvidenceAdd(e); }}
              maxLength={30}
              disabled={evidences.length >= 6}
            />
            <button type="button" className="bg-blue-500 text-white px-2 rounded" onClick={handleEvidenceAdd} disabled={evidenceInput.trim() === "" || evidences.length >= 6}>Añadir</button>
          </div>
          {evidences.length >= 6 && (
            <div className="text-xs text-red-600 mt-1">Máximo 6 evidencias.</div>
          )}
        </div>
        {/* Warnings */}
        {warnings.length > 0 && (
          <div className="mt-4 bg-yellow-50 border border-yellow-300 p-3 rounded">
            <b>Alineación pedagógica:</b>
            <ul className="list-disc pl-5">
              {warnings.map((w, i) => <li key={i} className="text-yellow-700">{w}</li>)}
            </ul>
            <button className="mt-2 text-xs bg-purple-600 text-white px-2 py-1 rounded" type="button" onClick={handleSuggestAlignment}>Corregir alineación con IA</button>
          </div>
        )}
        {/* Rubrica */}
        <div>
          <div className="flex items-center justify-between">
            <label className="font-semibold flex items-center gap-2">Rúbrica/criterios de evaluación</label>
            <button
              className="bg-purple-600 text-white px-4 py-2 rounded flex items-center gap-2"
              type="button"
              onClick={handleSuggestRubric}
              disabled={suggestingRubric || !title || !desc}
            >
              <span className="inline-block">⚡</span>
              {suggestingRubric ? "Generando..." : "Construir con IA"}
            </button>
          </div>
          <textarea
            className="w-full border rounded p-2"
            rows={4}
            placeholder={`Nivel 1 (Aprueba): ...\nNivel 2 (Destacado): ...\nNivel 3 (Excelente): ...`}
            value={rubric}
            onChange={e => setRubric(e.target.value)}
          />
        </div>
        {/* Submit */}
        <button className="bg-blue-600 text-white px-4 py-2 rounded w-full" type="submit" disabled={loading}>
          {loading ? "Generando..." : "Generar Markdown"}
        </button>
      </form>
      {/* Output */}
      {error && <div className="text-red-500 mt-2">{error}</div>}
      {markdown && (
        <div className="mt-8">
          <div className="flex gap-4 items-center mb-2">
            <h2 className="text-xl font-bold">Markdown generado</h2>
            <button className={`text-xs px-2 py-1 rounded ${showPreview ? "bg-gray-300" : "bg-blue-200"}`} type="button" onClick={() => setShowPreview(false)}>Markdown</button>
            <button className={`text-xs px-2 py-1 rounded ${showPreview ? "bg-blue-500 text-white" : "bg-gray-200"}`} type="button" onClick={() => setShowPreview(true)}>Preview</button>
          </div>
          {!showPreview ? (
            <textarea className="w-full border rounded p-2 font-mono" rows={12} value={markdown} readOnly />
          ) : (
            <div className="w-full border rounded p-4 bg-white prose max-w-none">
              <ReactMarkdown>{markdown}</ReactMarkdown>
            </div>
          )}
          <div className="flex gap-2 mt-2">
            <button className="bg-green-600 text-white px-3 py-1 rounded" onClick={copyMarkdown}>Copiar Markdown</button>
            <button className="bg-gray-200 text-gray-800 px-3 py-1 rounded" type="button" onClick={() => setShowIntegrationHelp(!showIntegrationHelp)}>
              ¿Cómo usar en Notion, Moodle o Google Docs?
            </button>
          </div>
        </div>
      )}
      {copied && (
        <div className="fixed bottom-6 right-6 bg-green-600 text-white px-4 py-2 rounded shadow-lg">¡Copiado!</div>
      )}
      {showIntegrationHelp && (
        <div className="mt-4 bg-blue-50 border border-blue-300 p-4 rounded text-sm">
          <b>¿Cómo usar este Markdown?</b>
          <ol className="list-decimal pl-5">
            <li>
              <b>Notion:</b> Crea una nueva página, pega el Markdown en un bloque, selecciona el texto y elige “Transformar en Markdown”.
            </li>
            <li>
              <b>Moodle:</b> En el editor, cambia a modo HTML/Markdown y pega el contenido. Si tu Moodle no soporta Markdown directo, usa un conversor online (Markdown ➔ HTML) y pega el resultado.
            </li>
            <li>
              <b>Google Docs:</b> Pega el Markdown y dale formato, o usa la extensión “Docs to Markdown” para importar/exportar.
            </li>
          </ol>
          <p className="mt-2">¡Listo! Así puedes reutilizar tus actividades en cualquier LMS/plataforma moderna.</p>
          <button className="mt-2 bg-blue-500 text-white px-3 py-1 rounded" type="button" onClick={() => setShowIntegrationHelp(false)}>
            Cerrar
          </button>
        </div>
      )}
    </main>
  );
}
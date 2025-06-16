export const bloomToEvidence: Record<string, string[]> = {
  "recordar": ["Quiz", "Preguntas de opción múltiple", "Lista de conceptos"],
  "comprender": ["Resumen", "Explicación oral", "Mapa conceptual"],
  "aplicar": ["Ejercicio práctico", "Simulación", "Resolución de problemas"],
  "analizar": ["Informe", "Análisis de caso", "Debate", "Presentación"],
  "evaluar": ["Ensayo crítico", "Debate", "Peer review", "Rúbrica"],
  "crear": ["Proyecto", "Diseño", "Prototipo", "Presentación final"],
  // agrega más si quieres
};

export function detectarVerboBloom(objetivo: string): string {
  const verbos = Object.keys(bloomToEvidence);
  for (const v of verbos) {
    if (objetivo.toLowerCase().startsWith(v)) return v;
    if (objetivo.toLowerCase().includes(v)) return v;
  }
  return "";
}

export function validarAlineacion(objectives: string[], evidences: string[]): string[] {
  const warnings: string[] = [];
  objectives.forEach(obj => {
    const verbo = detectarVerboBloom(obj);
    if (verbo) {
      const evidenciasSugeridas = bloomToEvidence[verbo];
      const found = evidences.some(ev =>
        evidenciasSugeridas.some(sug => ev.toLowerCase().includes(sug.toLowerCase()))
      );
      if (!found) {
        warnings.push(
          `⚠️ El objetivo "${obj}" sugiere evidencias como: ${evidenciasSugeridas.join(", ")}. Ninguna evidencia ingresada parece alineada.`
        );
      }
    }
  });
  return warnings;
}
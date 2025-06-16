#!/usr/bin/env python3
import typer
from rich.console import Console
from rich.markdown import Markdown
from core import load_strategies, render_strategy
import random
from llm_utils import infer_objectives

console = Console()

BLOOM_VERBS = [
    "Analizar", "Evaluar", "Diseñar", "Comparar", "Reflexionar", "Aplicar", "Identificar", "Crear", "Sintetizar"
]

def print_bloom_tip():
    console.print("\n[bold cyan]💡 Tip:[/bold cyan] Un buen objetivo de aprendizaje comienza con un verbo observable de la taxonomía de Bloom.")
    console.print("[green]Ejemplo:[/green] 'Analizar campañas exitosas de marketing de contenidos en PYMES.'")
    console.print("[yellow]Verbos de Bloom sugeridos:[/yellow] " + ", ".join(BLOOM_VERBS) + "\n")

def validate_objectives(objectives):
    validated = []
    for obj in objectives:
        if len(obj.strip()) < 8:
            console.print(f"[red]⚠️ Objetivo muy corto:[/red] {obj}")
            continue
        if not any(verb.lower() in obj.lower() for verb in BLOOM_VERBS):
            console.print(f"[red]⚠️ Objetivo sin verbo observable de Bloom:[/red] {obj}")
            continue
        validated.append(obj)
    return validated

app = typer.Typer()

@app.command()
def demo():
    """Ejecuta un ejemplo de actividad pre-cargada sin interacción."""
    activity_title = "Estrategia de Algoritmos de Búsqueda"
    activity_description = "Los estudiantes deberán implementar y comparar algoritmos de búsqueda en grafos, analizando su eficiencia en distintos escenarios."
    objectives = [
        "Analizar las diferencias entre algoritmos de búsqueda en grafos.",
        "Comparar la eficiencia de búsqueda en distintos escenarios.",
        "Aplicar algoritmos de búsqueda a problemas prácticos.",
        "Evaluar el rendimiento de los algoritmos implementados."
    ]
    strategy_id = "flipped"
    prework_instructions = "Revisar el capítulo sobre algoritmos de búsqueda antes de la clase."
    in_class_activity = "Resolver un set de ejercicios prácticos y discutir los resultados en grupo."

    strategies = load_strategies()
    strategy = next((s for s in strategies if s.id == strategy_id), None)

    context = {
        "activity_title": activity_title,
        "activity_description": activity_description,
        "learning_objectives": objectives,
        "prework_instructions": prework_instructions,
        "in_class_activity": in_class_activity,
        "expected_evidence": strategy.evidence,
        "implementation_notes": strategy.implementation_notes,
        "references": strategy.references,
    }

    output = render_strategy(strategy, context)
    console.print("\n[bold green]--- Demo: Markdown generado ---[/bold green]\n")
    console.print(Markdown(output))

@app.command()
def scaffold(
    strategy_id: str = typer.Option(..., help="ID de la estrategia (ej. 'flipped')"),
):
    """
    Genera un Markdown adaptado a la estrategia seleccionada, con validaciones y ayuda.
    """
    strategies = load_strategies()
    strategy = next((s for s in strategies if s.id == strategy_id), None)
    if not strategy:
        console.print(f"[red]Estrategia '{strategy_id}' no encontrada.[/red]")
        raise typer.Exit(1)

    activity_title = ""
    attempts = 0
    while not activity_title.strip():
        if attempts > 0:
            console.print("[yellow]Por favor, ingresa un título para la actividad.[/yellow]")
        activity_title = typer.prompt("Título de la actividad", default="")
        attempts += 1
        if attempts == 3 and not activity_title.strip():
            console.print("[bold cyan]Ejemplo:[/bold cyan] 'Marketing de Contenidos para PYMES'")
            activity_title = typer.prompt("Título de la actividad (puedes copiar el ejemplo)", default="")

    activity_description = ""
    attempts = 0
    while not activity_description.strip():
        if attempts > 0:
            console.print("[yellow]Por favor, ingresa una descripción para la actividad.[/yellow]")
        activity_description = typer.prompt("Descripción de la actividad", default="")
        attempts += 1
        if attempts == 3 and not activity_description.strip():
            console.print("[bold cyan]Ejemplo:[/bold cyan] 'Desarrollar estrategias de marketing digital para pequeñas empresas'")
            activity_description = typer.prompt("Descripción de la actividad (puedes copiar el ejemplo)", default="")

    print_bloom_tip()

    learning_objectives = ""
    attempts = 0
    while not learning_objectives.strip():
        if attempts > 0:
            console.print("[yellow]Intenta redactar al menos 2 objetivos separados por ';' (o deja vacío para sugerencia IA).[/yellow]")
        learning_objectives = typer.prompt(
            "Objetivos de aprendizaje (separa con ';', ENTER para sugerencia/autocompletar)", default=""
        )
        attempts += 1
        if attempts == 3 and not learning_objectives.strip():
            console.print("[bold cyan]Ejemplo:[/bold cyan] 'Analizar campañas exitosas de marketing; Evaluar impacto en ventas'")
            learning_objectives = typer.prompt("Objetivos de aprendizaje (puedes copiar el ejemplo o dejar vacío)", default="")
        if not learning_objectives.strip():
            typer.echo("\n🔮 ¿Quieres que te sugiera 3-4 objetivos basados en tu actividad usando IA? [y/N]")
            if typer.confirm("¿Usar IA para generar objetivos?", default=True):
                objectives = infer_objectives(activity_title, activity_description, n=4)
                # Fallback si respuesta es igual al prompt
                if (
                    len(objectives) == 1 and
                    ("Redacta" in objectives[0] or "objetivo" in objectives[0].lower())
                    or len(objectives[0]) < 25
                ):
                    console.print("⚠️ El modelo local no pudo generar objetivos útiles. Usando fallback.")
                    objectives = [
                        "Analizar conceptos clave del tema.",
                        "Aplicar conocimientos en un caso práctico.",
                        "Evaluar el impacto de la solución propuesta.",
                        "Reflexionar sobre el proceso de aprendizaje."
                    ]
                typer.echo("\nObjetivos sugeridos por IA:")
                for i, obj in enumerate(objectives, 1):
                    typer.echo(f"{i}. {obj}")
                if typer.confirm("¿Usar estos objetivos?", default=True):
                    learning_objectives = ";".join(objectives)
                else:
                    learning_objectives = typer.prompt("Escribe tus propios objetivos separados por ';'")
            else:
                # MVP: genera objetivos randomizados
                topic = activity_title.split()[0] if activity_title else "la temática"
                objectives = [
                    f"{random.choice(BLOOM_VERBS)} conceptos clave sobre {topic.lower()}",
                    f"{random.choice(BLOOM_VERBS)} casos prácticos de {topic.lower()}",
                    f"{random.choice(BLOOM_VERBS)} una propuesta creativa para {topic.lower()}",
                    f"{random.choice(BLOOM_VERBS)} el impacto de {topic.lower()} en contextos reales"
                ]
                console.print("Objetivos sugeridos:")
                for i, obj in enumerate(objectives, 1):
                    console.print(f"{i}. {obj}")
                if typer.confirm("¿Usar estos objetivos?", default=True):
                    learning_objectives = ";".join(objectives)
                else:
                    learning_objectives = typer.prompt("Escribe tus propios objetivos separados por ';'")

    objectives_list = [x.strip() for x in learning_objectives.split(";") if x.strip()]
    objectives_list = validate_objectives(objectives_list)
    if not objectives_list:
        console.print("[red]⚠️ No se ingresaron objetivos válidos. Se usarán ejemplos por defecto.[/red]")
        objectives_list = [
            "Analizar conceptos clave del tema.",
            "Aplicar conocimientos en un caso práctico.",
            "Evaluar el impacto de la solución propuesta.",
            "Reflexionar sobre el proceso de aprendizaje."
        ]

    prework_instructions = typer.prompt("Instrucciones de prework (solo para flipped, si aplica)", default="")
    in_class_activity = typer.prompt("Descripción de la actividad en clase (si aplica)", default="")

    context = {
        "activity_title": activity_title,
        "activity_description": activity_description,
        "learning_objectives": objectives_list,
        "prework_instructions": prework_instructions,
        "in_class_activity": in_class_activity,
        "expected_evidence": strategy.evidence,
        "implementation_notes": strategy.implementation_notes,
        "references": strategy.references,
    }

    output = render_strategy(strategy, context)
    console.print("\n[bold green]--- Generado Markdown ---[/bold green]\n")
    console.print(Markdown(output))

if __name__ == "__main__":
    app()
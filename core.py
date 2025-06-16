import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

class Strategy:
    def __init__(self, data):
        self.id = data["id"]
        self.display_name = data.get("display_name", self.id)
        self.description = data.get("description", "")
        self.taxonomies = data.get("taxonomies", [])
        self.nsm_metrics = data.get("nsm_metrics", [])
        self.evidence = data.get("evidence", [])
        self.implementation_notes = data.get("implementation_notes", "")
        self.references = data.get("references", [])
        self.template = data.get("template", "")

def load_strategies(yaml_path="strategies.yaml"):
    with open(yaml_path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    strategies = [Strategy(s) for s in doc["strategies"]]
    return strategies

def render_strategy(strategy, context):
    templates_dir = Path(__file__).parent / "strategies"
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template(strategy.template)
    return template.render(**context)
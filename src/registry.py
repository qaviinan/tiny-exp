import yaml

class MetricRegistry:
    def __init__(self, path="metrics.yaml"):
        with open(path, "r") as f:
            self.spec = yaml.safe_load(f)
        self.primary = self.spec["primary"]
        self.guardrails = self.spec.get("guardrails", [])
        self.defs = self.spec["definitions"]
        self.segments = self.spec.get("segments", [])

    def directions(self):
        # returns dict {metric: direction}
        d = {}
        for g in self.guardrails:
            d[g["name"]] = g.get("direction", "higher_is_better")
        d[self.primary] = "higher_is_better"
        return d

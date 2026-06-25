import yaml, os, copy
from pathlib import Path

_REQUIRED_KEYS = [
    ("theme", "mode"), ("theme", "colors"), ("timing", "animation_interval_ms"),
    ("algorithms", "scoring", "weight_waiting"), ("algorithms", "scoring", "weight_turnaround"),
    ("algorithms", "scoring", "weight_response"), ("algorithms", "scoring", "weight_cpu_idle"),
    ("algorithms", "scoring", "weight_context_switches"), ("algorithms", "scoring", "weight_fairness"),
    ("algorithms", "recommendation", "priority_spread_min"),
    ("algorithms", "recommendation", "rr_min_processes"),
    ("algorithms", "recommendation", "rr_arrival_span_min"),
    ("algorithms", "recommendation", "sjf_burst_variance_min"),
    ("algorithms", "recommendation", "sjf_avg_burst_max"),
    ("algorithms", "priority", "preemptive_slice"),
    ("algorithms", "defaults"), ("ui", "window"), ("ui", "gantt"), ("ui", "table"),
]

def _deep_get(d, keys):
    for k in keys:
        if not isinstance(d, dict) or k not in d: return None
        d = d[k]
    return d

def validate(data, path=()):
    if not isinstance(data, dict):
        raise ValueError(f"Expected dict at {'/'.join(path) or 'root'}, got {type(data).__name__}")
    for k, v in data.items():
        if isinstance(v, dict):
            validate(v, path + (k,))

def load_config(path=None):
    defaults_path = Path(__file__).parent / "defaults.yaml"
    with open(defaults_path) as f:
        cfg = yaml.safe_load(f)
    validate(cfg)
    if path and os.path.exists(path):
        with open(path) as f:
            overrides = yaml.safe_load(f)
        if overrides:
            validate(overrides)
            cfg = _deep_merge(cfg, overrides)
    for keys in _REQUIRED_KEYS:
        if _deep_get(cfg, keys) is None:
            raise ValueError(f"Missing required config key: {'/'.join(keys)}")
    return cfg

def _deep_merge(base, override):
    result = copy.deepcopy(base)
    for k, v in override.items():
        if k in result and isinstance(result[k], dict) and isinstance(v, dict):
            result[k] = _deep_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result

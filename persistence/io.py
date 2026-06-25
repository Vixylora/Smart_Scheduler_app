import json, csv
from core.process import Process

def export_json(processes, path):
    with open(path, 'w') as f:
        json.dump([p.to_dict() for p in processes], f, indent=2)

def import_json(path):
    with open(path) as f:
        return [Process.from_dict(d) for d in json.load(f)]

def export_csv(processes, path):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['PID', 'Arrival', 'Burst', 'Priority'])
        for p in processes:
            w.writerow([p.pid, p.arrival, p.burst, p.priority])

def import_csv(path):
    result = []
    with open(path, newline='') as f:
        for row in csv.DictReader(f):
            result.append(Process.validate(
                row['PID'], int(row['Arrival']), int(row['Burst']), int(row['Priority'])))
    return result

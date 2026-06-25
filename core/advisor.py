from core.algorithms import sanitize_processes
from core.scorer import calculate_score, fairness_penalty

def variance(values):
    if not values: return 0
    m = sum(values) / len(values)
    return sum((x - m) ** 2 for x in values) / len(values)

def recommend(processes, cfg):
    procs = sanitize_processes(processes)
    rec = cfg['algorithms']['recommendation']
    if not procs:
        return {'algorithm': 'FCFS', 'reason': 'No processes to schedule.'}
    bursts = [p.burst for p in procs]
    priorities = [p.priority for p in procs]
    arrivals = [p.arrival for p in procs]
    bv = variance(bursts)
    ps = max(priorities) - min(priorities)
    asp = max(arrivals) - min(arrivals)
    if ps >= rec['priority_spread_min']:
        return {'algorithm': 'Priority', 'reason': f'Priority spread ({ps}) exceeds threshold. Priority scheduling gives control to urgent jobs.'}
    if len(procs) >= rec['rr_min_processes'] or asp >= rec['rr_arrival_span_min']:
        return {'algorithm': 'Round Robin', 'reason': f'{len(procs)} processes with arrival span {asp}. Round Robin ensures fairness.'}
    ab = sum(bursts) / len(bursts)
    if bv >= rec['sjf_burst_variance_min'] or ab <= rec['sjf_avg_burst_max']:
        return {'algorithm': 'SJF', 'reason': f'Burst variance ({bv:.1f}) is high or avg burst ({ab:.1f}) is low. SJF minimizes wait time.'}
    return {'algorithm': 'FCFS', 'reason': 'Workload is simple and balanced. FCFS is the clearest fit.'}

def compare(processes, cfg):
    from core.algorithms import simulate
    algos = ['FCFS', 'SJF', 'Round Robin', 'Priority']
    opts = {'quantum': cfg['algorithms']['defaults']['quantum'],
            'priority_mode': cfg['algorithms']['defaults']['priority_mode'],
            'preemptive_slice': cfg['algorithms']['priority']['preemptive_slice'],
            'safety_guard': 10000}
    weights = cfg['algorithms']['scoring']
    results = []
    for algo in algos:
        r = simulate(processes, {**opts, 'algorithm': algo})
        fp = fairness_penalty(r['stats'])
        score = calculate_score(r, weights)
        results.append({'algorithm': algo, 'score': score, 'result': r, 'fairness_penalty': fp})
    return sorted(results, key=lambda x: x['score'])

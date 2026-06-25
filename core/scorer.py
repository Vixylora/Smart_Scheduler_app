def fairness_penalty(stats):
    if not stats: return 0
    avg = sum(s.waiting for s in stats) / len(stats)
    return sum(abs(s.waiting - avg) for s in stats) / len(stats)

def calculate_score(result, weights):
    return (
        result['averages']['waiting'] * weights['weight_waiting'] +
        result['averages']['turnaround'] * weights['weight_turnaround'] +
        result['averages']['response'] * weights['weight_response'] +
        (100 - result['cpu_utilization']) * weights['weight_cpu_idle'] +
        result['context_switches'] * weights['weight_context_switches'] +
        fairness_penalty(result['stats']) * weights['weight_fairness']
    )

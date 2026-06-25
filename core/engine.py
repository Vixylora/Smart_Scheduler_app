from functools import lru_cache
import threading
from core.algorithms import simulate
from core.advisor import recommend as _recommend

def _make_key(processes, algorithm, quantum, priority_mode, preemptive_slice):
    pdata = tuple(sorted((p.pid, p.arrival, p.burst, p.priority) for p in processes))
    return (pdata, algorithm, quantum, priority_mode, preemptive_slice)

class SimulationEngine:
    def __init__(self, cfg):
        self.cfg = cfg
        self._cache = {}
        self._comp_result = None
        self._comp_lock = threading.Lock()

    def _sim_opts(self, algorithm, quantum=None, priority_mode=None):
        d = self.cfg['algorithms']['defaults']
        return {'algorithm': algorithm,
                'quantum': quantum if quantum is not None else d['quantum'],
                'priority_mode': priority_mode if priority_mode is not None else d['priority_mode'],
                'preemptive_slice': self.cfg['algorithms']['priority']['preemptive_slice'],
                'safety_guard': 10000}

    def simulate(self, processes, algorithm=None, quantum=None, priority_mode=None):
        if algorithm is None: algorithm = self.cfg['algorithms']['defaults'].get('algorithm', 'FCFS')
        opts = self._sim_opts(algorithm, quantum, priority_mode)
        key = _make_key(processes, algorithm, opts['quantum'], opts['priority_mode'], opts['preemptive_slice'])
        if key not in self._cache:
            self._cache[key] = simulate(processes, opts)
        return self._cache[key]

    def compare(self, processes):
        with self._comp_lock:
            if self._comp_result is not None:
                return self._comp_result
        from core.advisor import compare
        result = compare(processes, self.cfg)
        with self._comp_lock:
            self._comp_result = result
        return result

    def recommend(self, processes):
        return _recommend(processes, self.cfg)

    def invalidate(self):
        self._cache.clear()
        with self._comp_lock:
            self._comp_result = None

    def auto_tune_interval(self, processes):
        dt = self.cfg['timing']['animation_interval_ms']
        s = self.simulate(processes)
        total = s.get('total_time', 0)
        if total > 50: return min(dt * 2, 2000)
        if total > 20: return dt
        return max(dt // 2, 200)

import math
from core.process import Process

def normalize_number(value, fallback=0):
    try:
        v = float(value)
        return v if math.isfinite(v) else fallback
    except (ValueError, TypeError):
        return fallback

class CircularQueue:
    def __init__(self, capacity=32):
        self._arr = [None] * capacity
        self._cap = capacity
        self._front = 0
        self._rear = 0
        self._size = 0

    def enqueue(self, item):
        if self._size == self._cap:
            self._resize()
        self._arr[self._rear] = item
        self._rear = (self._rear + 1) % self._cap
        self._size += 1

    def dequeue(self):
        if self._size == 0: return None
        item = self._arr[self._front]
        self._arr[self._front] = None
        self._front = (self._front + 1) % self._cap
        self._size -= 1
        return item

    def peek(self):
        return None if self._size == 0 else self._arr[self._front]

    def __len__(self): return self._size
    def __bool__(self): return self._size > 0

    def _resize(self):
        old = self._arr
        self._cap *= 2
        self._arr = [None] * self._cap
        for i in range(self._size):
            self._arr[i] = old[(self._front + i) % (self._cap // 2)]
        self._front = 0; self._rear = self._size

class LinkedList:
    class Node:
        __slots__ = ('value', 'next')
        def __init__(self, value):
            self.value = value
            self.next = None

    def __init__(self):
        self._head = None
        self._tail = None
        self._size = 0

    def append(self, value):
        node = self.Node(value)
        if self._tail:
            self._tail.next = node
            self._tail = node
        else:
            self._head = self._tail = node
        self._size += 1

    def pop_front(self):
        if self._head is None: return None
        val = self._head.value
        self._head = self._head.next
        if self._head is None: self._tail = None
        self._size -= 1
        return val

    def pop_at(self, index):
        if index < 0 or index >= self._size: return None
        if index == 0: return self.pop_front()
        prev = self._head
        for _ in range(index - 1):
            prev = prev.next
        val = prev.next.value
        prev.next = prev.next.next
        if prev.next is None: self._tail = prev
        self._size -= 1
        return val

    def peek(self, index=0):
        if index < 0 or index >= self._size: return None
        cur = self._head
        for _ in range(index): cur = cur.next
        return cur.value

    def __len__(self): return self._size
    def __bool__(self): return self._size > 0
    def __iter__(self):
        cur = self._head
        while cur:
            yield cur.value
            cur = cur.next

def sanitize_processes(process_list):
    if not process_list: return []
    sanitized = []
    for p in process_list:
        try:
            if isinstance(p, Process): sanitized.append(p.copy())
            elif isinstance(p, dict): sanitized.append(Process.from_dict(p))
            else: sanitized.append(Process.validate(p.pid, p.arrival, p.burst, p.priority))
        except Exception as e:
            print(f"Warning: Skipping invalid process {p}: {e}")
    sanitized.sort(key=lambda x: (x.arrival, x.pid))
    return sanitized

def simulate(processes, options):
    algorithm = options.get('algorithm', 'FCFS')
    quantum = max(1, normalize_number(options.get('quantum', 2)))
    priority_mode = options.get('priority_mode', 'Preemptive')
    pslice = options.get('preemptive_slice', 1)
    procs = sanitize_processes(processes)
    remaining = {p.pid: p.burst for p in procs}
    first_start, completion, timeline = {}, {}, []
    ready, time, idx, safety = LinkedList(), 0, 0, 0
    guard = options.get('safety_guard', 10000)

    def push():
        nonlocal idx
        while idx < len(procs) and procs[idx].arrival <= time:
            ready.append(procs[idx]); idx += 1

    def merge(pid, start, end):
        if start >= end: return
        last = timeline[-1] if timeline else None
        if last and last['pid'] == pid and last['end'] == start:
            last['end'] = end; return
        timeline.append({'pid': pid, 'start': start, 'end': end})

    def pick_burst():
        best_idx = 0
        best_val = None
        for i, p in enumerate(ready):
            if best_val is None or (p.burst, p.arrival, p.pid) < best_val:
                best_val = (p.burst, p.arrival, p.pid)
                best_idx = i
        return best_idx

    def pick_prio():
        best_idx = 0
        best_val = None
        for i, p in enumerate(ready):
            if best_val is None or (p.priority, p.arrival, p.pid) < best_val:
                best_val = (p.priority, p.arrival, p.pid)
                best_idx = i
        return best_idx

    cq = CircularQueue()

    while len(completion) < len(procs) and safety < guard:
        safety += 1
        if algorithm == 'Round Robin':
            while idx < len(procs) and procs[idx].arrival <= time:
                cq.enqueue(procs[idx]); idx += 1
            if not cq:
                na = procs[idx].arrival if idx < len(procs) else None
                if na is None: break
                merge('Idle', time, na); time = na; continue
            current = cq.dequeue()
        else:
            push()
            if not ready:
                na = procs[idx].arrival if idx < len(procs) else None
                if na is None: break
                merge('Idle', time, na); time = na; continue
            ci = 0
            if algorithm == 'SJF': ci = pick_burst()
            elif algorithm == 'Priority': ci = pick_prio()
            current = ready.pop_front() if ci == 0 else ready.pop_at(ci)

        rt = remaining[current.pid]
        if algorithm == 'Round Robin': sl = min(quantum, rt)
        elif algorithm == 'Priority' and priority_mode == 'Preemptive': sl = pslice
        else: sl = rt
        if current.pid not in first_start: first_start[current.pid] = time
        merge(current.pid, time, time + sl)
        time += sl; remaining[current.pid] = rt - sl

        if algorithm == 'Round Robin':
            while idx < len(procs) and procs[idx].arrival <= time:
                cq.enqueue(procs[idx]); idx += 1
            if remaining[current.pid] == 0: completion[current.pid] = time
            else: cq.enqueue(current)
        else:
            push()
            if remaining[current.pid] == 0: completion[current.pid] = time
            else: ready.append(current)

    stats = []
    for p in procs:
        f = completion.get(p.pid, time)
        ta = f - p.arrival
        w = ta - p.burst
        r = first_start.get(p.pid, p.arrival) - p.arrival
        p.turnaround, p.waiting, p.response, p.completion = ta, w, r, f
        stats.append(p)
    totals = {'waiting': sum(s.waiting for s in stats), 'turnaround': sum(s.turnaround for s in stats), 'response': sum(s.response for s in stats)}
    tt = timeline[-1]['end'] if timeline else 0
    bt = sum(s['end'] - s['start'] for s in timeline if s['pid'] != 'Idle')
    cs = sum(1 for i in range(1, len(timeline)) if timeline[i]['pid'] != timeline[i-1]['pid'])
    return {
        'algorithm': algorithm, 'quantum': quantum, 'priority_mode': priority_mode,
        'processes': procs, 'timeline': timeline, 'stats': stats, 'totals': totals,
        'averages': {'waiting': totals['waiting']/len(stats) if stats else 0,
                     'turnaround': totals['turnaround']/len(stats) if stats else 0,
                     'response': totals['response']/len(stats) if stats else 0},
        'throughput': len(stats)/tt if tt > 0 else 0,
        'cpu_utilization': (bt/tt*100) if tt > 0 else 0,
        'total_time': tt, 'busy_time': bt, 'context_switches': cs,
    }

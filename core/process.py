import copy

class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.priority = priority
        self.remaining = burst
        self.waiting = 0
        self.turnaround = 0
        self.response = 0
        self.completion = 0

    def __repr__(self):
        return f"{self.pid} (A:{self.arrival} B:{self.burst} P:{self.priority})"

    def copy(self):
        p = Process(self.pid, self.arrival, self.burst, self.priority)
        p.remaining = self.remaining
        p.waiting = self.waiting
        p.turnaround = self.turnaround
        p.response = self.response
        p.completion = self.completion
        return p

    @classmethod
    def validate(cls, pid, arrival, burst, priority):
        if not pid or not isinstance(pid, str):
            raise ValueError("PID must be a non-empty string")
        if not isinstance(arrival, (int, float)) or arrival < 0:
            raise ValueError("Arrival time must be a non-negative number")
        if not isinstance(burst, (int, float)) or burst < 1:
            raise ValueError("Burst time must be a positive number")
        if not isinstance(priority, (int, float)) or priority < 1:
            raise ValueError("Priority must be a positive integer")
        return cls(pid, arrival, burst, priority)

    @classmethod
    def from_dict(cls, data):
        return cls.validate(
            data.get('pid'),
            data.get('arrival', 0),
            data.get('burst', 1),
            data.get('priority', 1)
        )

    def to_dict(self):
        return {
            'pid': self.pid,
            'arrival': self.arrival,
            'burst': self.burst,
            'priority': self.priority
        }

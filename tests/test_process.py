from core.process import Process

def test_copy_independence():
    p = Process("P1", 0, 5, 2)
    c = p.copy()
    assert c.pid == p.pid and c.arrival == p.arrival and c.burst == p.burst and c.priority == p.priority
    assert c.remaining == 5 and c.waiting == 0
    c.remaining = 3; c.waiting = 2
    assert p.remaining == 5 and p.waiting == 0

def test_sanitize_creates_copies():
    plist = [Process("P1", 0, 5, 2), Process("P1", 1, 3, 3)]
    from core.algorithms import sanitize_processes
    out = sanitize_processes(plist)
    assert len(out) == 2
    assert out[0].pid == "P1"
    assert id(out[0]) != id(plist[0])

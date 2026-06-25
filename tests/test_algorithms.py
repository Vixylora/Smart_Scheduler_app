from core.algorithms import simulate, CircularQueue, LinkedList
from core.process import Process

OPTS = {'quantum':2,'priority_mode':'preemptive','preemptive_slice':1,'safety_guard':10000,'algorithm':'FCFS'}

def test_fcfs_basic():
    r = simulate([Process("P1",0,3,1), Process("P2",1,2,1)], OPTS)
    assert r['total_time'] == 5

def test_sjf():
    o = dict(OPTS, algorithm='SJF')
    r = simulate([Process("P1",0,5,1), Process("P2",0,3,1)], o)
    first = min(r['stats'], key=lambda s: s.completion)
    assert first.pid == 'P2'

def test_rr():
    o = dict(OPTS, algorithm='Round Robin')
    r = simulate([Process("P1",0,4,1), Process("P2",1,2,1)], o)
    assert r['context_switches'] >= 1

def test_priority_preemptive():
    o = dict(OPTS, algorithm='Priority')
    r = simulate([Process("P1",0,5,1), Process("P2",2,3,5)], o)
    assert r['total_time'] == 8

def test_non_preemptive():
    o = dict(OPTS, algorithm='FCFS', priority_mode='non-preemptive')
    simulate([Process("P1",0,3,1)], o)

def test_circular_queue():
    cq = CircularQueue(4)
    assert len(cq) == 0 and not cq
    cq.enqueue("a"); cq.enqueue("b"); cq.enqueue("c"); cq.enqueue("d")
    assert len(cq) == 4
    cq.enqueue("e")
    assert len(cq) == 5
    assert cq.dequeue() == "a"
    assert cq.dequeue() == "b"
    assert cq.dequeue() == "c"
    assert cq.dequeue() == "d"
    assert cq.dequeue() == "e"
    assert cq.dequeue() is None
    assert len(cq) == 0

def test_rr_circular_queue():
    o = dict(OPTS, algorithm='Round Robin')
    r = simulate([Process("P1",0,4,1), Process("P2",1,2,1)], o)
    tl = r['timeline']
    assert tl[0]['pid'] == 'P1'
    assert tl[-1]['end'] == r['total_time']

def test_linked_list():
    ll = LinkedList()
    assert len(ll) == 0 and not ll
    ll.append("a"); ll.append("b"); ll.append("c")
    assert len(ll) == 3
    assert list(ll) == ["a", "b", "c"]
    assert ll.pop_front() == "a"
    assert ll.pop_front() == "b"
    assert ll.pop_at(0) == "c"
    assert ll.pop_front() is None
    ll.append("x"); ll.append("y")
    assert ll.pop_at(1) == "y"
    assert ll.pop_front() == "x"

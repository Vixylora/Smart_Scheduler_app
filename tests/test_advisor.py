from core.advisor import recommend
from core.process import Process

def _cfg():
    return {'algorithms':{'recommendation':{'priority_spread_min':2,'rr_min_processes':4,'rr_arrival_span_min':3,'sjf_burst_variance_min':5,'sjf_avg_burst_max':4}}}

def test_recommend_fcfs():
    cfg = _cfg()
    procs = [Process("P1",0,6,1), Process("P2",1,6,1)]
    r = recommend(procs, cfg)
    assert r['algorithm'] == 'FCFS'

def test_recommend_priority():
    cfg = _cfg()
    procs = [Process("P1",0,2,5), Process("P2",1,3,1)]
    r = recommend(procs, cfg)
    assert r['algorithm'] == 'Priority'

def test_recommend_rr():
    cfg = _cfg()
    procs = [Process(f"P{i}",i,2,1) for i in range(4)]
    r = recommend(procs, cfg)
    assert r['algorithm'] == 'Round Robin'

def test_recommend_sjf():
    cfg = _cfg()
    procs = [Process("P1",0,1,1), Process("P2",1,2,1)]
    r = recommend(procs, cfg)
    assert r['algorithm'] == 'SJF'

def test_recommend_empty():
    cfg = _cfg()
    assert recommend([], cfg)['algorithm'] == 'FCFS'

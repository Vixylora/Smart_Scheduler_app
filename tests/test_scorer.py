from core.scorer import calculate_score, fairness_penalty

def _mock_stat(wait=0, turn=0, resp=0, comp=0):
    class S: pass
    s = S(); s.waiting=wait; s.turnaround=turn; s.response=resp; s.completion=comp
    return s

def test_fairness_penalty_zero():
    assert fairness_penalty([_mock_stat(5), _mock_stat(5), _mock_stat(5)]) == 0.0

def test_fairness_penalty_nonzero():
    fp = fairness_penalty([_mock_stat(0), _mock_stat(10)])
    assert fp == 5.0

def test_calculate_score():
    w = {'weight_waiting':1,'weight_turnaround':1,'weight_response':1,'weight_cpu_idle':1,'weight_context_switches':1,'weight_fairness':1}
    r = {'averages':{'waiting':5,'turnaround':10,'response':3},'cpu_utilization':80,'context_switches':12,
         'stats':[_mock_stat(5,10,3,15),_mock_stat(7,12,4,18)]}
    score = calculate_score(r, w)
    assert score > 0

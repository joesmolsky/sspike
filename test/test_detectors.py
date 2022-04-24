from sspike.detectors import Detector


def test_Detector():
    detector = Detector("kamland")
    assert detector.name == "kamland"
    assert detector.N_p == 6.02582603699751e31
    assert detector.N_e == 2.438651797172892e32
    assert detector.low_cut == 2e-4

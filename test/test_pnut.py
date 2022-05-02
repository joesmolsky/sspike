from math import isclose

from sspike.supernova import Supernova
from sspike.detectors import Detector
from sspike import pnut

model = "Nakazato_2013"
progenitor = {"mass": 20, "metal": 0.02, "t_rev": 300}
transformation = "NoTransformation"
distance = 5.0
sn = Supernova(model, progenitor, transformation, distance)
detector = Detector("kamland")


def test_get_luminosities():
    lum = pnut.get_luminosities(sn)
    assert list(lum.keys()) == ["time", "NU_E", "NU_E_BAR", "NU_X", "NU_X_BAR"]
    assert lum["time"][0] == -0.05
    assert lum["time"][390] == 20.0


def test_get_fluences():
    fluences = pnut.get_fluences(sn)
    assert list(fluences.keys()) == [
        "E",
        "NuE",
        "NuMu",
        "NuTau",
        "aNuE",
        "aNuMu",
        "aNuTau",
    ]
    assert len(fluences["E"]) == 501
    assert fluences["NuTau"][0] == 3.78587055e09


def test_snowglobes_events():
    key_list = [
        "unsmeared_unweighted_0",
        "smeared_unweighted_0",
        "unsmeared_weighted_0",
        "smeared_weighted_0",
    ]
    column_list = ["Energy", "ibd", "nue_C12", "nue_C13", "nuebar_C12", "nc", "e"]
    snow_events = pnut.snowglobes_events(sn, detector)
    assert list(snow_events.keys()) == key_list
    assert list(snow_events[key_list[0]].keys()) == column_list
    assert snow_events["smeared_weighted_0"]["Energy"][0] == 0.0007488
    assert snow_events["smeared_weighted_0"]["Energy"][199] == 0.09975


def test_sspike_events():
    key_list = ["basic_0", "elastic_0"]
    column_list = [
        "T_p",
        "E_vis",
        "E_min",
        "nc_nue_p",
        "nc_nuebar_p",
        "nc_nux_p",
        "nc_nuxbar_p",
        "nc_p",
    ]
    close = 1e-6
    E0 = 4.812395531670816e-06
    E174 = 0.0008421692180423
    sspike_events = pnut.sspike_events(sn, detector)
    assert list(sspike_events.keys()) == key_list
    assert list(sspike_events["elastic_0"].keys()) == column_list
    assert sspike_events["elastic_0"]["T_p"][0] == 0.0001
    assert sspike_events["elastic_0"]["T_p"][174] == 0.0175

    assert isclose(sspike_events["elastic_0"]["E_vis"][0], E0, rel_tol=close)
    assert isclose(sspike_events["elastic_0"]["E_vis"][174], E174, rel_tol=close)

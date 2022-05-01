from sspike.supernova import Supernova

model = "Nakazato_2013"
progenitor = {"mass": 20, "metal": 0.02, "t_rev": 300}
transformation = "NoTransformation"
distance = 3.14
sn = Supernova(model, progenitor, transformation, distance)


def test_Supernova_keys():
    assert sn.model == "Nakazato_2013"
    assert sn.progenitor == {"mass": 20, "metal": 0.02, "t_rev": 300}
    assert sn.transform == "NoTransformation"
    assert sn.distance == 3.14
    assert sn.sn_name == "N13-20-20-300"
    assert sn.t_min == -0.05
    assert sn.t_max == 20.0


def test_bin_times():
    ts, tm, te = sn.bin_times()

    assert ts.value[0] == -0.05
    assert tm.value[0] == 9.975
    assert te.value[0] == 20.0

    for t in (ts, tm, te):
        assert str(t.unit) == "s"

def test_random_df():
    df = sn.random_df()
    keys = list(df.keys())

    assert len(df) == 1
    assert keys[0] == 0.000749
    assert keys[199] == 0.09975

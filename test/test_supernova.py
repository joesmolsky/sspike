from sspike.supernova import Supernova

model = 'Nakazato_2013'
progenitor = {'mass': 20,
              'metal': 0.02,
              't_rev': 300}
transformation = 'NoTransformation'
distance = 5.
sn = Supernova(model, progenitor, transformation, distance)


def test_Supernova_keys():
    assert sn.model == 'Nakazato_2013'
    assert sn.progenitor == {'mass': 20,
                             'metal': 0.02,
                             't_rev': 300}
    assert sn.transform == 'NoTransformation'
    assert sn.distance == 5.
    assert sn.sn_name == 'N13-20-20-300'
    assert sn.t_min == -0.05
    assert sn.t_max == 20.

def test_Supernova_record():
    assert isinstance(sn.get_record(), dict)

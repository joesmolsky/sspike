from sspike.snowball import Snowball

model = 'Nakazato_2013'
progenitor = {'mass': 20,
              'metal': 0.02,
              't_rev': 300}
transformation = 'NoTransformation'
distance = 5
sb = Snowball(model, progenitor, transformation, distance)


def test_Snowball_keys():
    assert sb.model == 'Nakazato_2013'
    assert sb.progenitor == {'mass': 20,
                             'metal': 0.02,
                             't_rev': 300}
    assert sb.transform == 'NoTransformation'
    assert sb.distance == 5
    assert sb.tarball == '/Users/joe/src/snewpy/models'\
                         '/Nakazato_2013/N13-20-20-300.tar.bz2'


def test_fluences():
    fluences = sb.fluences()
    assert (fluences.keys() == ['E', 'NuE', 'NuMu', 'NuTau', 'aNuE', 'aNuMu', 'aNuTau']).all()
    assert len(fluences['E']) == 501
    assert fluences['NuTau'][0] == 3785870550.0

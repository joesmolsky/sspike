from sspike.snowball import Snowball
from sspike.detectors import Detector
from sspike import pnut

model = 'Nakazato_2013'
progenitor = {'mass': 30,
              'metal': 0.02,
              't_rev': 100}
transformation = 'NoTransformation'
distance = 5

sb = Snowball(model, progenitor, transformation, distance)
detector = Detector('kamland')


def test_snowglobes_events():
    snowflakes = pnut.snowglobes_events(sb, detector)
    assert snowflakes[0] == '/Users/joe/src/gitjoe/sspike/out/snowballs'\
                            '/N13-30-20-100/5kpc-NoTransformation'\
                            '/snow-unsmeared.csv'
    assert snowflakes[1] == '/Users/joe/src/gitjoe/sspike/out/snowballs'\
                            '/N13-30-20-100/5kpc-NoTransformation'\
                            '/snow-smeared.csv'


def test_sspike_events():
    sspikes = pnut.sspike_events(sb, detector)
    assert sspikes[0] == '/Users/joe/src/gitjoe/sspike/out/snowballs'\
                         '/N13-30-20-100/5kpc-NoTransformation/'\
                         'sspike-basic.csv'
    assert sspikes[1] == '/Users/joe/src/gitjoe/sspike/out/snowballs'\
                         '/N13-30-20-100/5kpc-NoTransformation/'\
                         'sspike-nc.csv'

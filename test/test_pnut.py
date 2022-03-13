from sspike.snowball import Snowball
from sspike.targets import Target
from sspike import pnut

model = 'Nakazato_2013'
progenitor = {'mass': 30,
              'metal': 0.02,
              't_rev': 100}
transformation = 'NoTransformation'
distance = 5

sb = Snowball(model, progenitor, transformation, distance)
target = Target('kamland')


def test_snowglobes_events():
    snowflakes = pnut.snowglobes_events(sb, target)
    assert snowflakes[0] == '/Users/joe/src/gitjoe/sspike/snowballs'\
                            '/N13-30-20-100/5kpc-NoTransformation'\
                            '/snow-unsmeared.csv'
    assert snowflakes[1] == '/Users/joe/src/gitjoe/sspike/snowballs'\
                            '/N13-30-20-100/5kpc-NoTransformation'\
                            '/snow-smeared.csv'


def test_sspike_events():
    sspikes = pnut.sspike_events(sb, target)
    assert sspikes[0] == '/Users/joe/src/gitjoe/sspike/snowballs'\
                         '/N13-30-20-100/5kpc-NoTransformation/'\
                         'sspike-basic.csv'
    assert sspikes[1] == '/Users/joe/src/gitjoe/sspike/snowballs'\
                         '/N13-30-20-100/5kpc-NoTransformation/'\
                         'sspike-nc.csv'

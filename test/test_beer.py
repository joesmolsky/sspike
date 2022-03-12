from sspike.beer import draw, tab
from sspike.snowball import Snowball
from sspike.targets import Target

# Directory of copied data from working version.
data_dir = '/Users/joe/src/gitjoe/sspike/test/test_data/'
# Data file types.
smeared = 'snow-smeared.csv'
unsmeared = 'snow-unsmeared.csv'
basic = 'sspike-basic.csv'
nc = 'sspike-nc.csv'
# Directory for test plot outputs.
plot_dir = '/Users/joe/src/gitjoe/sspike/test/plots/'

# Target instance for channel names.
target = Target('kamland')


# SNOwGLoBES unsmeared plot.
def test_draw_unsmeared():
    draw(f'{data_dir}{unsmeared}', channels=target.snow_channels,
         save=f'{plot_dir}{unsmeared[:-3]}', test=True)


# SNOwGLoBES smeared plot.
def test_draw_smeared():
    draw(f'{data_dir}{smeared}', channels=target.snow_channels,
         save=f'{plot_dir}{smeared[:-3]}', test=True)


def test_draw_basic():
    draw(f'{data_dir}{basic}', channels=target.basic_channels,
         save=f'{plot_dir}{basic[:-3]}', test=True)


def test_draw_nc():
    draw(f'{data_dir}{nc}', channels=target.nc_channels,
         save=f'{plot_dir}{nc[:-3]}', test=True)


# Testing Snowball
model = 'Nakazato_2013'
progenitor = {'mass': 20,
              'metal': 0.02,
              't_rev': 300}
transformation = 'NoTransformation'
distance = 5
sb = Snowball(model, progenitor, transformation, distance)


def test_tab():
    tab(sb)

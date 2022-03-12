from sspike.beer import draw
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
from os.path import isdir

from sspike.env import models_dir, snowglobes_dir, sspike_dir


def test_env():
    for d in [models_dir, snowglobes_dir, sspike_dir]:
        assert isdir(d)

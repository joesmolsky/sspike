from sspike.supernova import Supernova
from sspike.detectors import Detector
from sspike import beer

model = "Nakazato_2013"
progenitor = {"mass": 20, "metal": 0.02, "t_rev": 300}
transformation = "NoTransformation"
distance = 3.14
sn = Supernova(model, progenitor, transformation, distance)
detector = Detector("kamland")


def test_plot_luminosities():
    beer.plot_luminosities(sn, show=False)


def test_plot_fluences():
    beer.plot_fluences(sn, show=False)


def test_plot_snowglobes_events():
    beer.plot_snowglobes_events(sn, detector, with_unsmeared=False, show=False)
    beer.plot_snowglobes_events(sn, detector, with_unsmeared=True, show=False)


def test_plot_sspike_events():
    beer.plot_sspike_events(sn, detector, show=False)


def test_bar_totals():
    beer.bar_totals(sn, detector, show=False)


def test_bar_vis():
    beer.bar_vis(sn, detector, show=False)

"""Nakazato supernovae simulation events in KamLAND.

Load a Nakazato simulation using snewpy.  Process with SNOwGLoBES for standard
channels and sspike for proton elastic scattering.
"""

from sspike import pnut, beer


def main():
    """Process with snewpy and spike."""
    # Set detector.  Only option is 'kamland' for now.
    detector = 'kamland'
    # Distance to supernova in kpc.
    distance = 0.6
    # Set simulation type.  Only option is 'Nakazato_2013' for now.
    model = 'Nakazato_2013'
    # Nakazato simulation parameters.
    # Progenitor mass in solar masses.  Options: 13, 20, 30, 50.
    # Metalicity.  Options: 0.02 (solar), 0.004 (small magellanic cloud).
    # Revival time in milliseconds.  Options: 100, 200, 300.
    progenitor = {'mass': 20,
                  'metal': 0.02,
                  'rev': 300}
    # Neutrino transformation type.  Only option is 'NoTransformation for now.
    transform = 'NoTransformation'

    # pnut: predict neutrino underground telemetry.
    snowball = pnut.get_fluence(model, progenitor, transform, distance)
    snowflakes = pnut.snowglobes_events(snowball, detector)
    sspiked = pnut.elastic_events(snowball, detector)

    # beer: back-end event reader.
    events = beer.combo(sspiked, snowflakes)
    beer.save(events)
    beer.display(events)

main()
from sspike.detectors import Detector


def test_Detector():
    detector = Detector('kamland')
    assert detector.name == 'kamland'
    assert detector.N_p == 6.02582603699751e+31
    assert detector.N_e == 2.438651797172892e+32
    assert detector.snow_channels == ['ibd', 'nue_e', 'nuebar_e', 'numu_e',
                                    'numubar_e', 'nutau_e', 'nutaubar_e',
                                    'nue_C12', 'nuebar_C12', 'nc_nue_C12',
                                    'nc_nuebar_C12', 'nc_numu_C12',
                                    'nc_numubar_C12', 'nc_nutau_C12',
                                    'nc_nutaubar_C12', 'nue_C13', 'nc_nue_C13',
                                    'nc_numu_C13', 'nc_nutau_C13',
                                    'nc_nuebar_C13', 'nc_numubar_C13',
                                    'nc_nutaubar_C13']
    assert detector.basic_channels == ['ibd', 'nue_e', 'nuebar_e', 'nux_e']
    assert detector.nc_channels == ['nc_nue_p', 'nc_nuebar_p',
                                  'nc_nux_p', 'nc_nuxbar_p']

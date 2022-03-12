from sspike.targets import Target


def test_Target():
    target = Target('kamland')
    assert target.name == 'kamland'
    assert target.N_p == 6.02582603699751e+31
    assert target.N_e == 2.438651797172892e+32
    assert target.snow_channels == ['ibd', 'nue_e', 'nuebar_e', 'numu_e',
                                    'numubar_e', 'nutau_e', 'nutaubar_e',
                                    'nue_C12', 'nuebar_C12', 'nc_nue_C12',
                                    'nc_nuebar_C12', 'nc_numu_C12',
                                    'nc_numubar_C12', 'nc_nutau_C12',
                                    'nc_nutaubar_C12', 'nue_C13', 'nc_nue_C13',
                                    'nc_numu_C13', 'nc_nutau_C13',
                                    'nc_nuebar_C13', 'nc_numubar_C13',
                                    'nc_nutaubar_C13']
    assert target.basic_channels == ['ibd', 'nue_e', 'nuebar_e', 'nux_e']
    assert target.nc_channels == ['nc_nue_p', 'nc_nuebar_p',
                                  'nc_nux_p', 'nc_nuxbar_p']

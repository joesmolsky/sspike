import subprocess


def test_sspike():
    sspike_com = ['sspike', 'Nakazato_2013', '-D', '10',
                  '-M', '20', '-Z', '0.02', '-R', '200']
    assert subprocess.check_output(sspike_com) == b"Starting simulation.\n"\
                                                  b"Job's done.\n"

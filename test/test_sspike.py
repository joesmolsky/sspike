import subprocess


def test_sspike():
    sspike_com = ['sspike', 'Nakazato_2013', '-D', '10',
                  '-M', '20', '-Z', '0.02', '-R', '200']
    assert subprocess.check_output(sspike_com) == b"Job's done.\n"

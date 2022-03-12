import subprocess


def test_sspike():
    assert subprocess.check_output(['sspike', '-d']) == b"Job's done.\n"

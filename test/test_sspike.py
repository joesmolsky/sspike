import subprocess


def test_sspike():
    # Run Nakazato model from command line.
    sspike_com = [
        "sspike",
        "Nakazato_2013",
        "-L",
        "5",
        "-M",
        "20",
        "-Z",
        "0.02",
        "-R",
        "300",
    ]

    # Expected print statements.
    output = (
        b"Starting simulation: Nakazato_2013 \t "
        b"{'mass': '20', 'metal': 0.02, 't_rev': '300'}.\n"
        b"Job's done.\n"
    )

    assert subprocess.check_output(sspike_com) == output

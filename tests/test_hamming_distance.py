import HammingDistanceCalculator


def test_get_hello_msg():
    assert cli.get_hello_msg() == "Hello World!"
    assert cli.get_hello_msg("Bioinformagician") == "Hello Bioinformagician!"

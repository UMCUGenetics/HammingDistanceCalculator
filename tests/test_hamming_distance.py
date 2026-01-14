import pytest
from hammingdistancecalculator.hamming_distance import (
    hamming_distance,
    is_valid_dna,
    rev_comp,
    is_valid_input_csv,
    load_barcodes,
    compare_sample_barcode_list
)

# test hamming distance function
@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("A", "A", 0),                      # distance of 0, identical letters
        ("a", "a", 0),                      # distance of 0, lowe case
        ("a", "A", 0),                      # distance of 0, mixed case
        ("C", "T", 1),                      # distance of 1, 1 letter difference
        ("c", "t", 1),                      # distance of 1, lower case
        ("C", "t", 1),                      # distance of 1, mixed case
        ("ACTGCG", "ACTGCG", 0),            # distance of 0, multiple letters
        ("actgcg", "actgcg", 0),            # distance of 0, lower case
        ("ACTGCG", "actgcg", 0),            # distance of 0, mixed case
        ("AACCGGTT", "TTGGCCAA", 8),        # distance of 6, full mismatch
        ("aaccttgg", "ttggccaa", 8),        # distance of 6, full mismatch
        ("AACCGGTT", "ttggccaa", 8),        # distance of 6, full mismatch
    ],
)
def test_hamming_distance(a, b, expected):
    # test normal cases
    assert hamming_distance(a, b) == expected


def test_hamming_distance_empty():
    # test empty strings
    with pytest.raises(ValueError, match=r"^Invalid letter found in sequences:"):
        hamming_distance("", "")


# test valid and invalid DNA sequences
@pytest.mark.parametrize(
    "seq,expected",
    [
        ("A", True),            # Single valid character
        ("ACTG", True),         # All valid characters
        ("AAA", True),          # Repeated valid characters
        ("", False),            # Empty string should be invalid
        ("ACTGN", False),       # Contains 'N' which is not allowed
        ("XYZ", False),         # Completely invalid characters
        ("actg", False),        # Lowercase letters should fail (regex expects uppercase)
        ("ACTG123", False),     # Numbers are not allowed
        ("ACTG!", False),       # Special characters are not allowed
    ]
)
def test_is_valid_dna(seq, expected):
    assert is_valid_dna(seq) == expected

# test rev_comp
def test_rev_comp():
    # default
    assert rev_comp("ATCG") == "CGAT"

    # palindrome
    assert rev_comp("ATAT") == "ATAT"

# test is_valid_input_csv
def test_is_valid_input_csv():
    bad_file = 'tests/bad_input.csv'
    good_file = 'tests/good_input.csv'

    assert is_valid_input_csv(good_file)

    with pytest.raises(ValueError, match="has too many elements, 2 expected\.$"):
        is_valid_input_csv(bad_file)


# test load_barcodes
def test_load_barcodes_correct(tmp_path):
    test_file = tmp_path / 'barcodes.csv'
    test_file.write_text("label,barcode\n"
                         "S1,ACTG\n"
                         "S2,TTTT",
                         encoding="utf-8")

    test_barcodes = load_barcodes(test_file)
    assert test_barcodes == [("S1", "ACTG"),("S2", "TTTT")]


def test_load_barcodes_strips_whitespace(tmp_path):
    test_file2 = tmp_path / 'barcodes2.csv'
    test_file2.write_text("label,barcode\n"
                          "S1,ACTG      \n"
                          "S2,TTTT    ",
                          encoding="utf-8")

    test_barcodes2 = load_barcodes(test_file2)
    assert test_barcodes2 == [("S1", "ACTG"), ("S2", "TTTT")]


def test_load_barcodes_invalid_csv_raises_exception(tmp_path):
    test_file3 = tmp_path / 'barcodes2.csv'
    test_file3.write_text("label,barcode\n"
                          "S1,ACXX\n"
                          "S2,",
                          encoding="utf-8")

    # invalid second row should throw a value error (but from is_valid_input_csv as its triggered first)
    with pytest.raises(ValueError, match="^Invalid DNA-letters found in label "):
        load_barcodes(test_file3)


# test compare_sample_barcode_list
def test_compare_sample_barcode_list_with_mocked_tpqm(mocker):
    test_set = [
        ("S1", "ACTG"),
        ("S2", "ACCG"),
        ("S3", "TTTT")
    ]

    # Create a mock object that behaves like a tqdm context manager
    progress_mock = mocker.MagicMock()
    tqdm_mock = mocker.MagicMock()
    tqdm_mock.return_value = progress_mock
#    tqdm_mock.return_value.__enter__.return_value = progress_mock

    # patch the function we want to mock
    mocker.patch("hammingdistancecalculator.hamming_distance.tqdm", tqdm_mock)

    # store the return function so we can compare to the expected values
    return_value = compare_sample_barcode_list(test_set)

    #
    # # compare expected keys to return value
    # expected_keys = {
    #     "S1_vs_S2",
    #     "S1_vs_revcomp_S2",
    #     "S1_vs_S3",
    #     "S1_vs_revcomp_S3",
    #     "S2_vs_S3",
    #     "S2_vs_revcomp_S3"
    # }
    #
    # # check the keys are correct
    # assert set(return_value.keys()) == expected_keys

    # compare expected values to return values
    expected_values = {
        "S1_vs_S2": 1,
        "S1_vs_revcomp_S2": 4,
        "S1_vs_S3": 3,
        "S1_vs_revcomp_S3": 3,
        "S2_vs_S3": 4,
        "S2_vs_revcomp_S3": 3,
    }

    # assert key set
    assert set(return_value.keys()) == set(expected_values.keys())

    # assert exact values
    assert return_value == expected_values

    # create tqdm & update it while going over the items
    # N = 3 -> total = N * (N - 1) = 6
    tqdm_mock.assert_called_once_with(total=6, desc="Compare_barcodes", unit="cmp")
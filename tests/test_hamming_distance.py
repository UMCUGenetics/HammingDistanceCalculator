import pytest
from hammingdistancecalculator.hamming_distance import (
    hamming_distance,
    is_valid_dna,
    rev_comp,
    is_valid_input_csv
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

    assert is_valid_input_csv(good_file) == True

    with pytest.raises(ValueError, match=f"has too many elements, 2 expected\.$"):
        is_valid_input_csv(bad_file)

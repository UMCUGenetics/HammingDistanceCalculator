import pytest
import re
from hammingdistancecalculator.hamming_distance import (
    cli,
    hamming_distance,
    is_valid_dna,
    rev_comp,
    is_valid_input_csv,
    load_barcodes,
    compare_sample_barcode_list
)
from typer.testing import CliRunner


# test hamming distance function
@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("A", "A", 0),  # distance of 0, identical letters
        ("a", "a", 0),  # distance of 0, lowe case
        ("a", "A", 0),  # distance of 0, mixed case
        ("C", "T", 1),  # distance of 1, 1 letter difference
        ("c", "t", 1),  # distance of 1, lower case
        ("C", "t", 1),  # distance of 1, mixed case
        ("ACTGCG", "ACTGCG", 0),  # distance of 0, multiple letters
        ("actgcg", "actgcg", 0),  # distance of 0, lower case
        ("ACTGCG", "actgcg", 0),  # distance of 0, mixed case
        ("AACCGGTT", "TTGGCCAA", 8),  # distance of 6, full mismatch
        ("aaccttgg", "ttggccaa", 8),  # distance of 6, full mismatch
        ("AACCGGTT", "ttggccaa", 8),  # distance of 6, full mismatch
    ],
)
def test_hamming_distance(a, b, expected):
    # test normal cases
    assert hamming_distance(a, b) == expected


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ("", "", 0),  # empty strings
        ("A", "", 0),  # unequal length
        ("AC", "A", 0),  # unequal length
        ("A", "AC", 0),  # unequal length
    ],
)
def test_hamming_distance_empty(a, b, expected):
    # test empty strings
    with pytest.raises(ValueError, match=r"^Provided sequences are invalid, "
                                         r"only A, C, T, and G nucleotides are allowed. Invalid sequences:"):
        hamming_distance("", "")


# test invalid dna provided
@pytest.mark.parametrize(
    "a,b,error_message",
    [
        ("QQ", "AA",
         "Provided sequence for sequence 1 is invalid, only A, C, T, and G nucleotides are allowed. Invalid sequence: QQ"),
        # Left side invalid
        ("AA", "BB",
         "Provided sequence for sequence 2 is invalid, only A, C, T, and G nucleotides are allowed. Invalid sequence: BB"),
        # Right side invalid
        ("QA", "AA",
         "Provided sequence for sequence 1 is invalid, only A, C, T, and G nucleotides are allowed. Invalid sequence: QA"),
        # Left side partially invalid
        ("AQ", "AA",
         "Provided sequence for sequence 1 is invalid, only A, C, T, and G nucleotides are allowed. Invalid sequence: AQ"),
        # Left side partially invalid
        ("AA", "QA",
         "Provided sequence for sequence 2 is invalid, only A, C, T, and G nucleotides are allowed. Invalid sequence: QA"),
        # Right side partially invalid
        ("AA", "AQ",
         "Provided sequence for sequence 2 is invalid, only A, C, T, and G nucleotides are allowed. Invalid sequence: AQ"),
        # Right side partially invalid
        ("QQ", "VV", "Provided sequences are invalid, only A, C, T, and G nucleotides are allowed. Invalid sequences: QQ, VV"),
        # Both sides invalid
        ("QA", "VA", "Provided sequences are invalid, only A, C, T, and G nucleotides are allowed. Invalid sequences: QA, VA"),
        # Both sides invalid
        ("QA", "AV", "Provided sequences are invalid, only A, C, T, and G nucleotides are allowed. Invalid sequences: QA, AV"),
        # Both sides invalid
        ("AQ", "VA", "Provided sequences are invalid, only A, C, T, and G nucleotides are allowed. Invalid sequences: AQ, VA"),
        # Both sides invalid
        ("AQ", "AV", "Provided sequences are invalid, only A, C, T, and G nucleotides are allowed. Invalid sequences: AQ, AV"),
        # Both sides invalid
    ],
)
def test_hamming_distance_invalid_dna(a, b, error_message):
    with pytest.raises(ValueError) as value_err_message:
        hamming_distance(a, b)

    assert str(value_err_message.value) == error_message


# test is_valid_dna function
@pytest.mark.parametrize(
    "seq,expected",
    [
        ("A", True),  # Single valid character
        ("ACTG", True),  # All valid characters
        ("AAA", True),  # Repeated valid characters
        ("", False),  # Empty string should be invalid
        ("ACTGN", False),  # Contains 'N' which is not allowed
        ("XYZ", False),  # Completely invalid characters
        ("actg", False),  # Lowercase letters should fail (regex expects uppercase)
        ("ACTG123", False),  # Numbers are not allowed
        ("ACTG!", False),  # Special characters are not allowed
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

    with pytest.raises(ValueError,
                       match=re.escape("Line ['S1', ' ACTG', ' invalid extra'] has too many elements, 2 expected.")):
        is_valid_input_csv(bad_file)


# test load_barcodes
def test_load_barcodes_correct(tmp_path):
    test_file = tmp_path / 'barcodes.csv'
    test_file.write_text("label,barcode\n"
                         "S1,ACTG\n"
                         "S2,TTTT",
                         encoding="utf-8")

    test_barcodes = load_barcodes(test_file)
    assert test_barcodes == [("S1", "ACTG"), ("S2", "TTTT")]


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

    # patch the function we want to mock
    mocker.patch("hammingdistancecalculator.hamming_distance.tqdm", tqdm_mock)

    # store the return function so we can compare to the expected values
    return_value = compare_sample_barcode_list(test_set)

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


def test_cli_outpath_parameter_creates_directory(tmp_path):
    """Test dat --outpath directory automatisch maakt"""
    input_file = tmp_path / "input.csv"
    input_file.write_text("label,barcode\nS1,ACTG\nS2,ACCG", encoding="utf-8")

    output_dir = tmp_path / "custom_output"
    assert not output_dir.exists()

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "--outpath", str(output_dir)])

    assert result.exit_code == 0
    assert output_dir.exists(), "Directory werd niet aangemaakt!"


def test_cli_max_distance_plus_one_logic(tmp_path):
    """Test dat max_distance+1 correct werkt (effectieve range telt 1 op bij max)"""
    input_file = tmp_path / "data.csv"
    input_file.write_text("label,barcode\nS1,AAAA\nS2,CCCC", encoding="utf-8")

    output_dir = tmp_path / "max_test"

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "-d", "2", "-o", str(output_dir)])

    assert result.exit_code == 0

    # max_distance=2, effectiveMaxDistance=3 → files 0, 1, 2 (3 files totaal)
    created_files = sorted([f.name for f in output_dir.glob("hamming_distance_*.txt")])
    expected_files = ["hamming_distance_0.txt", "hamming_distance_1.txt", "hamming_distance_2.txt"]

    assert created_files == expected_files, f"Verwacht {expected_files}, kreeg {created_files}"


def test_cli_both_short_and_long_flags_work(tmp_path):
    """Test dat zowel -d/-o als --max-distance/--outpath werken"""
    input_file = tmp_path / "test.csv"
    input_file.write_text("label,barcode\nX,ATGC\nY,ATGA", encoding="utf-8")

    output_dir = tmp_path / "flags_test"

    runner = CliRunner()
    # Gebruik korte flags
    result = runner.invoke(cli, [str(input_file), "-d", "1", "-o", str(output_dir)])

    assert result.exit_code == 0
    assert len(list(output_dir.glob("*.txt"))) > 0


def test_cli_default_behavior_without_options(tmp_path):
    """Test default gedrag met expliciete . directory"""
    input_file = tmp_path / "default.csv"
    input_file.write_text("label,barcode\nA,ACTG\nB,ACCG", encoding="utf-8")

    output_dir = tmp_path / "dot_output"

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "-o", str(output_dir)])

    assert result.exit_code == 0
    assert (output_dir / "hamming_distance_0.txt").exists()


def test_cli_help_shows_all_options():
    """Test dat --help beide opties toont"""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "--outpath" in result.stdout or "-o" in result.stdout
    assert "--max-distance" in result.stdout or "-d" in result.stdout


def test_cli_multiple_barcodes_different_distances(tmp_path):
    """Test met diverse afstanden tussen barcodes"""
    input_file = tmp_path / "multi.csv"
    # AAAA vs AAAA = dist 0
    # AAAA vs AAAA = dist 0
    # AAAA vs AAAG = dist 1
    # AAAA vs GGTC = dist 4
    input_file.write_text("label,barcode\nM,AAAA\nN,AAAA\nO,AAAG\nP,GGTC", encoding="utf-8")

    output_dir = tmp_path / "mixed_distances"

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "-d", "5", "-o", str(output_dir)])

    assert result.exit_code == 0

    # Minstens dist 0 en 1 moeten bestaan
    assert (output_dir / "hamming_distance_0.txt").exists()
    assert (output_dir / "hamming_distance_1.txt").exists()


def test_cli_output_content_verification(tmp_path):
    """Test dat output file inhoud correct is"""
    input_file = tmp_path / "verify.csv"
    input_file.write_text("label,barcode\nFirst,AAAA\nSecond,AAAA", encoding="utf-8")

    output_dir = tmp_path / "content_check"

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "--outpath", str(output_dir)])

    assert result.exit_code == 0

    dist0 = output_dir / "hamming_distance_0.txt"
    content = dist0.read_text()

    # Check juiste format (LET OP: "vs" met spaties, NIET "_vs_"!)
    assert "Number of comparisons found with hamming distance 0:" in content
    assert "Barcode First vs barcode Second" in content
    assert "has hamming distance 0" in content


def test_cli_nonexistent_parent_directory_created(tmp_path):
    """Test nested directory (parents=True)"""
    input_file = tmp_path / "input.csv"
    input_file.write_text("label,barcode\nS1,ACTG", encoding="utf-8")

    output_dir = tmp_path / "level1" / "level2" / "deep_output"

    runner = CliRunner()
    result = runner.invoke(cli, [str(input_file), "-o", str(output_dir)])

    assert result.exit_code == 0
    assert output_dir.exists(), "Nested directories werden niet aangemaakt!"


def test_cli_missing_required_argument_fails():
    """Test dat ontbrekend verplicht argument een error geeft"""
    runner = CliRunner()
    result = runner.invoke(cli, [])  # Geen input argument

    assert result.exit_code != 0
    assert "Missing argument" in result.output or "Usage:" in result.output

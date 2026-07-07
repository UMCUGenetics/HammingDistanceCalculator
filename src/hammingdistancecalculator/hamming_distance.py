import re
import typer
import csv
from pathlib import Path
from tqdm import tqdm
from collections import defaultdict

# create typer object
cli = typer.Typer()


# define hamming distance function
def hamming_distance(seq1: str, seq2: str) -> int:
    """This function calculates the hamming distance between two barcode sequences.

    Args:
        seq1: First sequence for comparison
        seq2: Second sequence for comparison

    Returns:
        distance_counter: The calculated hamming distance.

    """

    # stop if no str type provided
    if not isinstance(seq1, str) or not isinstance(seq2, str):
        raise TypeError("seq1 and/or seq2 are not of type str.")

    # remove whitespace (if present) and move to uppercase if needed
    seq1 = seq1.strip().upper()
    seq2 = seq2.strip().upper()

    # check for invalid letters in each dna sequence separately and combined
    check_1 = is_valid_dna(seq1)
    check_2 = is_valid_dna(seq2)
    if not check_1 and not check_2:
        raise ValueError(
            f'Provided sequences are invalid, only A, C, T, and G nucleotides are allowed. Invalid sequences: {seq1}, {seq2}')
    elif not check_1 and check_2:
        raise ValueError(
            f'Provided sequence for sequence 1 is invalid, only A, C, T, and G nucleotides are allowed. '
            f'Invalid sequence: {seq1}')
    elif check_1 and not check_2:
        raise ValueError(
            f'Provided sequence for sequence 2 is invalid, only A, C, T, and G nucleotides are allowed. '
            f'Invalid sequence: {seq2}')

    # break if index have unequal length
    if len(seq1) != len(seq2):
        raise ValueError("Strings must be of equal length")

    # define a distance counter to store hamming_distance letter by letter until we get the full hamming distance
    distance_counter = 0

    # use zip to iterate faster and more pythonic
    for character_left, character_right in zip(seq1, seq2):
        if character_left != character_right:
            distance_counter += 1
    return distance_counter


def is_valid_dna(seq: str) -> bool:
    """Check if provided dna string contains valid characters
    Currently only 'A', 'C', 'T' and 'G' are checked for.

    Args:
        seq: The String provided to test for valid DNA letters

    Returns:
        bool: Boolean stating if the input dna is valid or not

    """
    return bool(re.fullmatch(r"[ACTG]+", seq))


def rev_comp(dna: str) -> str:
    """Function which returns the reverse complement of a DNA string
    Args:
        dna: The input DNA string we want to convert

    Returns:
        reverse_comp: The reverse complement of the input DNA string

    """
    rev_dict = {'A': 'T',
                'C': 'G',
                'G': 'C',
                'T': 'A'}
    return "".join(rev_dict[n] for n in reversed(dna))


def is_valid_input_csv(csv_file: Path) -> bool:
    """Function that tests input csv file given to be in the expected format.
    We expect the file to have a header with labels 'label', 'barcode'.
    We expect no empty labels
    We expect no empty barcodes

    Args:
        csv_file: The input file to use

    Returns:
        bool: Returns a boolean to show if the input is valid or not

    """
    with (open(csv_file, 'r') as file_handle):

        # expect the first line to be the header
        header_line = file_handle.readline().strip().lower()

        # validate header
        if header_line != 'label,barcode':
            raise ValueError(f"Expected header with 'label, barcode', but found {header_line}")

        # expect the rest to be the body
        for row_values in file_handle:
            line = row_values.strip().split(',')
            # check number of elements per line
            if len(line) > 2:
                raise ValueError(f"Line {line} has too many elements, 2 expected.")

            label = str(line[0])
            sequence = str(line[1].upper())

            # check for empty lines
            if label == "":
                raise ValueError("Found an empty label.")
            if sequence == "":
                raise ValueError(f"Found an empty barcode for label: {label}")

            # check if the DNA contains valid letters
            if not is_valid_dna(sequence.strip()):
                raise ValueError(f"Invalid DNA-letters found in label '{label}': {sequence}")

    return True


def load_barcodes(input_csv: Path) -> list[tuple[(str, str)]]:
    """Load in the input csv file and store this as a list of tuples (label, barcode)

    Args:
        input_csv: The input csv file to load

    Returns:
        list[tuple[(str, str)]]: A list of tuples, of barcode - dna combinations

    """
    # validate input
    if is_valid_input_csv(input_csv):
        pass

    # loop over input, skip header and store as list of tuples
    barcode_records = list()
    with open(input_csv, 'r') as file_handle:
        # skip first row (header)
        next(file_handle)

        # then process the rest
        for row_values in file_handle:
            label, sample = row_values.strip().split(',')
            record = (str(label), str(sample))
            barcode_records.append(record)

    return barcode_records


def compare_sample_barcode_list(sample_barcode_list: list) -> dict:
    """Compare all barcodes with all barcodes and calculate hamming distance

    This an all vs all comparison, so each barcode(or DNA sequence) found is compared against all other barcodes/sequences.

    Args:
        sample_barcode_list: list of tuples with format 'label, barcode'

    Returns:
        dict: Dictionary with hamming distances between each barcode
    """
    result_dict = {}

    labels = [label for label, _ in sample_barcode_list]
    sequences = [sequence for _, sequence in sample_barcode_list]
    reverse_complements = [rev_comp(sequence) for sequence in sequences]

    sequence_count = len(sequences)
    total_number_of_comparisons = sequence_count * (sequence_count - 1)

    # compare loop with tqdm, so it shows a progress bar (useful for large input datasets)
    with tqdm(total=total_number_of_comparisons, desc="Compare_barcodes", unit="cmp") as progress_bar:
        for left_index in range(sequence_count):
            label_left = labels[left_index]
            sequence_left = sequences[left_index]

            for right_index in range(left_index + 1, sequence_count):
                label_right = labels[right_index]
                sequence_right = sequences[right_index]

                # forward-forward comparison
                distance_forward = hamming_distance(sequence_left, sequence_right)
                comparison_key = f"{label_left}_vs_{label_right}"
                result_dict[comparison_key] = distance_forward
                progress_bar.update(1)

                # forward-revcomp comparison
                distance_revcomp = hamming_distance(sequence_left, reverse_complements[right_index])
                comparison_key = f"{label_left}_vs_revcomp_{label_right}"
                result_dict[comparison_key] = distance_revcomp
                progress_bar.update(1)

    return result_dict


# main script
@cli.command()
def main(input_csv: Path = typer.Argument(help="Pad naar input CSV met kolommen: label,barcode"),
         max_distance: int = typer.Option(
             1,
             "--max-distance",
             "-d",
             help="Maximale hamming distance waarvoor output wordt geschreven (default op 1, wat 0 & 1 schrijft)."
         ),
         outpath: Path = typer.Option(
             ".",
             "--outpath",
             "-o",
             help="Directory waar output files worden geschreven (default huidige directory)."
         )):
    # read input
    sample_barcode_list = load_barcodes(input_csv)

    # compare all barcodes
    # create dict with key: label_A_vs_label_B
    # and value: hamming_distance
    compare_dict = compare_sample_barcode_list(sample_barcode_list)

    # create a dict with labels for each hamming distance.
    # here we store label : hamming distance as key:value,
    # which means all labels with hamming distance 0 are in index 0
    # all labels with hamming distance 1 are in index 1 etc.
    hamming_distance_dict = defaultdict(list)
    for key, value in compare_dict.items():
        hamming_distance_dict[value].append(key)

    # verify output path exists to write to
    outpath.mkdir(parents=True, exist_ok=True)

    # add 1 to the max distance because when you want a range of 1, you want to loop 'including' 1, not 'until' 1
    effective_max_distance = max_distance + 1

    # write output files for all distances of 0 to effective_max_distance (2 by default)
    for counter in range(effective_max_distance):
        output_path = outpath / f"hamming_distance_{counter}.txt"

        # write each file
        with output_path.open('w', newline='') as file_handle:
            writer = csv.writer(file_handle)
            writer.writerow(
                [f"Number of comparisons found with hamming distance {counter}: {len(hamming_distance_dict[counter])}"])

            for item in hamming_distance_dict[counter]:
                writer.writerow(
                    [f"Barcode {item.split('_vs_')[0]} vs barcode {item.split('_vs_')[1]} has hamming distance {counter}"])


if __name__ == "__main__":
    cli()

import pathlib
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
    """
    This function calculates the hamming distance between two barcode sequences.

    :param seq1: The first index used
    :type seq1: str
    :param seq2: The index to compare to
    :type seq2: str
    :return: The hamming distance between the two distances
    :rtype: int
    """
    # stop if no str type provided
    if not isinstance(seq1, str) or not isinstance(seq2, str):
        raise TypeError("seq1 and/or seq2 are not of type str.")

    # remove whitespace (if present) and move to uppercase if needed
    seq1 = seq1.strip().upper()
    seq2 = seq2.strip().upper()

    # check for invalid letters
    if not (is_valid_dna(seq1) and is_valid_dna(seq2)):
        raise ValueError(f'Invalid letter found in sequences: {seq1}, {seq2}')

    # break if index have unequal length
    if len(seq1) != len(seq2):
        raise ValueError("Strings must be of equal length")

    # define a counter
    distance_counter = 0

    # use zip to iterate faster and more pythonic
    for character_left, character_right in zip(seq1, seq2):
        if character_left != character_right:
            distance_counter += 1
    return distance_counter

def is_valid_dna(seq: str) -> bool:
    """
    Check if provided dna string contains valid characters

    :param seq: input string
    :return: boolean true/false
    """
    return bool(re.fullmatch(r"[ACTG]+", seq))


def rev_comp(dna: str) -> str:
    """
    Function which returns the reverse complement of a DNA string

    :param dna:
    :type dna: string
    :return: returns rev complement
    :rtype: str
    """
    rev_dict = {'A': 'T',
                'C': 'G',
                'G': 'C',
                'T': 'A'}
    return "".join(rev_dict[n] for n in reversed(dna))


def is_valid_input_csv(csv_file: Path) -> bool:
    """
    Function that tests input csv file given to be in the expected format.
    We expect the file to have a header with labels 'label', 'barcode'.
    We expect no empty labels
    We expect no empty barcodes
    :param csv_file:
    """
    with open(csv_file, 'r') as file_handle:
        # expect the first line to be the header
        all_lines = file_handle.readlines()

        headerline = all_lines[0].strip().lower()
        bodylines = all_lines[1:]

        if headerline != 'label,barcode':
            raise ValueError(f"Expected header with 'label, barcode', but found {headerline}")

        for row_values in bodylines:
            line = row_values.split(',')
            # check number of elements per line
            print(f"line: {line}")
            if len(line) > 2:
                raise ValueError(f"Line {line} has too many elements, 2 expected.")

            potential_label = str(line[0])
            potential_sequence = str(line[1].upper())

            # check for empty lines
            if potential_label == "":
                raise ValueError("Found an empty label.")
            if potential_sequence == "":
                raise ValueError(f"Found an empty barcode for label: {potential_label}")

            # check if the DNA contains valid letters
            if not is_valid_dna(potential_sequence.strip()):
                raise ValueError(f"Invalid DNA-letters found in label '{potential_label}': {potential_sequence}")

    return True


def load_barcodes(input_csv: Path) -> list[tuple[(str, str)]]:
    """
    Load in the input csv file and store this as a list of tuples (label, barcode)
    :param input_csv: filename of input csv
    """
    # validate input
    if is_valid_input_csv(input_csv):
        pass

    # loop over input, skip header and store as list of tuples
    barcode_records = list()
    with open(input_csv, 'r') as f:
        lines = f.readlines()[1:]

        for row in lines:
            label, sample = row.split(',')
            record = (str(label), str(sample.strip()))
            barcode_records.append(record)

    return barcode_records


def compare_sample_barcode_list(sample_barcode_list: list) -> dict:
    """
    Compare all barcodes with all barcodes and calculate hamming distance

    :param sample_barcode_list: list of tuples with format 'label, barcode'
    :return: dict with key: comparison, value: hamming_distance
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

                # forward-revcomp
                distance_revcomp = hamming_distance(sequence_left, reverse_complements[right_index])
                comparison_key = f"{label_left}_vs_revcomp_{label_right}"
                result_dict[comparison_key] = distance_revcomp
                progress_bar.update(1)

    return result_dict



# main script
@cli.command()
def main(input_csv: Path = typer.Argument(help="Pad naar input CSV met kolommen: label,barcode")):

    # read input
    sample_barcode_list = load_barcodes(input_csv)

    # compare all barcodes
    # maak dict met key: label_A_vs_label_B
    # en value: hamming_distance
    compare_dict = compare_sample_barcode_list(sample_barcode_list)

    # debug
    #print(f'compare dict: {compare_dict}')

    # sort output based on hamming distance
    sorted_dict = defaultdict(list)
    for key, value in compare_dict.items():
        sorted_dict[value].append(key)

    distance_0 = sorted_dict[0]
    distance_1 = sorted_dict[1]

    # write output
    output_path_hamming_0 = pathlib.Path('hamming_distance_0.txt')
    output_path_hamming_1 = pathlib.Path('hamming_distance_1.txt')

    # dist 0
    print("Writing barcodes with hamming distance 0...")
    with output_path_hamming_0.open('w', newline='') as file_handle:
        writer = csv.writer(file_handle)
        writer.writerow([f"Number of comparisons found with hamming distance 0: {len(distance_0)}"])
        for item in distance_0:
            writer.writerow([f"Barcode {item.split('_vs_')[0]} vs barcode {item.split('_vs_')[1]} has hamming distance 0"])

    # dist 1
    print("Writing barcodes with hamming distance 1...")
    with output_path_hamming_1.open('w', newline='') as file_handle:
        writer = csv.writer(file_handle)
        writer.writerow([f"Number of comparisons found with hamming distance 1: {len(distance_1)}"])
        for item in distance_1:
            writer.writerow([f"Barcode {item.split('_vs_')[0]} vs barcode {item.split('_vs_')[1]} has hamming distance 1"])


if __name__ == "__main__":
    cli()

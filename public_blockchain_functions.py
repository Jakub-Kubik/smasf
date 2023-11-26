"""Module contains function for
plotting public blockchain after simulation.

Author: Jan Jakub Kubik (xkubik32)
Date: 10.4.2023
"""
from typing import Dict, List, Union

import matplotlib.pyplot as plt


def plot_block_counts(block_counts: Dict[str, int], miners_info: List[float]) -> None:
    """
    Plots the percentage of blocks mined by each miner.

    Args:
        block_counts (Dict[str, int]): A dictionary with miner names as keys and
                                       the number of blocks mined as values.
        miners_info (List[float]): A list of mining powers for each miner.

    Returns:
        None
    """
    miner_names = list(block_counts.keys())
    total_blocks = sum(block_counts.values())
    block_percentages = [
        100 * block_counts[name] / total_blocks for name in miner_names
    ]

    mining_powers = miners_info
    mining_power_labels = [f"{power:.1f}%" for power in mining_powers]

    bars = plt.bar(miner_names, block_percentages)

    for bar_new, label, miner_name in zip(bars, mining_power_labels, miner_names):
        height = bar_new.get_height()
        block_count = block_counts[miner_name]
        plt.text(
            bar_new.get_x() + bar_new.get_width() / 2,
            height,
            f"{label}\n{block_count} blocks",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    plt.xlabel("Miner")
    plt.ylabel("Percentage of Blocks Mined")
    plt.title(
        f"Percentage of Blocks Mined by Each Miner (Mining Power and Block "
        f"Count on Top of Bars)\nTotal Blocks: {total_blocks}"
    )
    plt.show()


def float_with_comma(number: float) -> str:
    """
    Convert a float number to a string and replace the decimal point with a comma.

    Args:
        number (float): The input float number to convert.

    Returns:
        str: The converted string with the decimal point replaced by a comma.
    """
    return str(number).replace(".", ",")


def calculate_percentage(
    block_counts: Dict[str, dict], total_blocks: int, ratio: int
) -> Dict[str, float]:
    """
    Calculate the percentage of blocks mined by each miner.

    Args:
        block_counts (Dict[str, int]): A dictionary with miner names as keys and the
                             number of blocks mined as values.
        total_blocks (int): The total number of blocks mined.

    Returns:
        Dict[str, float]: A dictionary with miner names as keys and their corresponding percentage
              of blocks mined as values.
    """
    return {
        miner: round((block_counts[miner]["strong"] + (block_counts[miner]["weak"] / (ratio - 1))) / total_blocks * 100, 3)
        for miner in block_counts
    }


# pylint: disable=too-many-arguments
def print_attackers_success(
    block_counts: Dict[str, int],
    percentages: Dict[str, float],
    winns: Dict[int, Union[int, float]],
    attacker_ids: List[int],
    block_counts_same: Dict[str, int] = None,
    is_strongchain: bool = False,
) -> None:
    """
    Print the success information of attackers.

    Args:
        block_counts (Dict[str, int]): A dictionary with miner names as keys and the number of
                             blocks mined as values.
        percentages (Dict[str, float]): A dictionary with miner names as keys and their
                                        corresponding percentage of blocks mined as values.
        winns (Dict[int, Union[int, float]]): A dictionary with miner IDs as keys and
                                              their corresponding winn values.
        attacker_ids (List[int]): A list of attacker IDs.
        block_counts_same (Dict[str, int], optional): A dictionary with miner names as keys
                        and the number of blocks mined as values for the same mining strategy.
        is_strongchain (bool, optional): A flag to indicate if the mining strategy is
                                        strongchain. Defaults to False.

    Returns:
        None
    """
    for attacker_id in attacker_ids:
        attacker_name = f"Selfish miner {attacker_id}"
        success = percentages[attacker_name]
        print("-------------")
        print(float_with_comma(success))
        print(winns[attacker_id])

        if is_strongchain:
            print(block_counts_same[f"{attacker_name} weak"])
            print(block_counts_same[f"{attacker_name} strong"])
        else:
            print(block_counts[attacker_name])


# pylint: disable=too-many-arguments
def print_honest_miner_info(
    block_counts: Dict[str, int],
    percentages: Dict[str, float],
    winns: Dict[int, Union[int, float]],
    miner_id: int,
    block_counts_same: Dict[str, int] = None,
    is_strongchain: bool = False,
) -> None:
    """
    Print the success information of an honest miner.

    Args:
        block_counts (Dict[str, int]): A dictionary with miner names as keys and the number
                                       of blocks mined as values.
        percentages (Dict[str, float]): A dictionary with miner names as keys and their
                                        corresponding percentage of blocks mined as values.
        winns (Dict[int, Union[int, float]]): A dictionary with miner IDs as keys and their
                                              corresponding winn values.
        miner_id (int): The ID of the honest miner.
        block_counts_same (Dict[str, int], optional): A dictionary with miner names as keys and
                the number of blocks mined as values for the same mining strategy.
        is_strongchain (bool, optional): A flag to indicate if the mining strategy is strongchain.
                                         Defaults to False.

    Returns:
        None
    """
    miner_name = f"Honest miner {miner_id}"
    for name, suc in percentages.items():
        if "Honest" in name:
            success = suc

    print("-------------")
    print(float_with_comma(round(success, 3)))
    print(winns[miner_id])
    print(block_counts_same)
    print(miner_name)

    if is_strongchain:
        print(block_counts_same[f"{miner_name} weak"])
        print(block_counts_same[f"{miner_name} strong"])
    else:
        print(block_counts[miner_name])

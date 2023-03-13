"""Module contains Mediator class which can run
whole simulation of selfish mining for Subchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 13.3.2023
"""
from base.logs import create_logger


def run():
    """Run function."""
    log = create_logger("subchain")
    log.info("Mediator in Subchain")

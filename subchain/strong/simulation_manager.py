"""Module contains Mediator class which can run
whole simulation of selfish mining for Subchain consensus.

Author: Jan Jakub Kubik (xkubik32)
Date: 23.3.2023
"""

import random

from base.miner_base import MinerType
from nakamoto.simulation_manager import SimulationManager as NakamotoSimulationManager
from public_blockchain_functions import (
    calculate_percentage,
    plot_block_counts,
    print_attackers_success,
    print_honest_miner_info,
)
from subchain.sim_config import SimulationConfig
from subchain.strong.blockchain import Blockchain
from subchain.strong.honest_miner import HonestMinerStrategy
from subchain.strong.selfish_miner import SelfishMinerStrategy


class SimulationManager(NakamotoSimulationManager):
    """Mediator class for Subchain consensus for running whole simulation."""

    def __init__(self, simulation_config: dict, blockchain: str):
        super().__init__(
            simulation_config, blockchain
        )  # create everything necessary from Nakamoto

        self.honest_miner = HonestMinerStrategy(mining_power=self.config.honest_miner)
        self.selfish_miners = [
            SelfishMinerStrategy(mining_power=sm_power)
            for sm_power in self.config.selfish_miners
        ]
        self.miners = [self.honest_miner] + self.selfish_miners
        self.miners_info = [self.honest_miner.mining_power] + [
            sm.mining_power for sm in self.selfish_miners
        ]

        self.public_blockchain = Blockchain(owner="public blockchain")

    def parse_config(self, simulation_config):
        """Parsing dict from yaml config."""
        self.log.info("Subchain parse config method")

        sim_config = self.general_config_validations(
            simulation_config, ["weak_to_strong_block_ratio"]
        )
        return SimulationConfig(
            consensus_name=sim_config["consensus_name"],
            honest_miner=sim_config["miners"]["honest"]["mining_power"],
            selfish_miners=[
                sm["mining_power"] for sm in sim_config["miners"]["selfish"]
            ],
            gamma=sim_config["gamma"],
            simulation_mining_rounds=sim_config["simulation_mining_rounds"],
            weak_to_strong_block_ratio=sim_config["weak_to_strong_block_ratio"],
        )

    def resolve_matches_clear(self, winner):
        winner.clear_private_strong_chain()
        # clear private weak chain of selfish miner
        self.honest_miner.clear_private_weak_chain()

    def resolve_overrides_clear(self, match_obj):
        match_obj.clear_private_strong_chain()
        # need to clear weak blockchain of honest miner
        self.honest_miner.clear_private_weak_chain()

    def add_honest_block(self, round_id, honest_miner, is_weak_block):
        self.public_blockchain.chain.extend(honest_miner.blockchain_weak.chain)
        honest_miner.clear_private_weak_chain()
        super().add_honest_block(round_id, honest_miner, is_weak_block)

        self.public_blockchain.last_strong_block_id = len(self.public_blockchain.chain)

    def selfish_override(self, leader):
        # override public blockchain by attacker's private blockchain
        self.ongoing_fork = False
        self.log.info(
            f"Override by attacker {leader.blockchain.fork_block_id},"
            f" {leader.miner_id} in fork"
        )
        self.public_blockchain.override_chain(leader)
        # cleaning of competing SM is performed via ADOPT
        leader.clear_private_strong_chain()
        # cleaning of competing SM is performed via ADOPT
        # clear just honest miner private weak chain
        self.honest_miner.clear_private_weak_chain()

    def run_simulation(self):
        """Main business logic for running selfish mining simulation."""
        self.winns = {
            miner.miner_id: 0 for miner in self.selfish_miners + [self.honest_miner]
        }

        total_blocks = self.config.weak_to_strong_block_ratio + 1
        weak_block_probability = self.config.weak_to_strong_block_ratio / total_blocks
        weak_blocks = 0
        strong_blocks = 0

        for blocks_mined in range(self.config.simulation_mining_rounds):
            leader = self.choose_leader(self.miners, self.miners_info)
            self.winns[leader.miner_id] += 1

            random_number = random.random()
            if random_number <= weak_block_probability:
                print(
                    f"Weak block generated in round {blocks_mined} by {leader.miner_type}"
                )
                miner_str = (
                    "Honest" if leader.miner_type == MinerType.HONEST else "Selfish"
                )
                leader.blockchain_weak.add_block(
                    data=f"Block {blocks_mined} data",
                    miner=f"{miner_str} miner {leader.miner_id}",
                    miner_id=leader.miner_id,
                    is_weak=True,
                )
                weak_blocks += 1

            else:
                print(
                    f"Strong block generated in round {blocks_mined} by {leader.miner_type}"
                )
                self.one_round(leader, blocks_mined, is_weak_block=False)
                strong_blocks += 1

        print(f"number of weak blocks: {weak_blocks}")
        print(
            f"Their probability: {(weak_blocks / (weak_blocks + strong_blocks)) * 100}%"
        )
        print(f"number of strong blocks: {strong_blocks}")
        print(
            f"Their probability: {(strong_blocks / (weak_blocks + strong_blocks) * 100)}%"
        )

    def run(self):
        self.log.info("Mediator in Subchain STRONG blocks")

        self.run_simulation()

        block_counts = {f"Honest miner {self.honest_miner.miner_id}": 0}
        for miner in self.selfish_miners:
            block_counts.update({f"Selfish miner {miner.miner_id}": 0})

        for block in self.public_blockchain.chain:
            block_counts[block.miner] += 1

        attacker_ids = [
            miner.miner_id for miner in self.selfish_miners
        ]  # List of attacker IDs
        honest_miner_id = self.honest_miner.miner_id  # Honest miner ID

        total_blocks = sum(block_counts.values())
        percentages = calculate_percentage(block_counts, total_blocks)
        print_attackers_success(block_counts, percentages, self.winns, attacker_ids)
        print_honest_miner_info(block_counts, percentages, self.winns, honest_miner_id)

        # self.log.info(block_counts)
        # self.log.info(self.selfish_miners[0].blockchain.chain)

        plot_block_counts(block_counts, self.miners_info)

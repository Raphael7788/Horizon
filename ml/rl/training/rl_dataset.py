#!/usr/bin/env python3

import gzip
import json
from datetime import datetime

import numpy as np


class RLDataset:
    def __init__(self, file_path):
        """
        Holds a collection of RL samples.

        :param file_path: String Load/save the dataset from/to this file.
        """
        self.file_path = file_path
        self.rows = []
        self.pre_timeline_format_rows = []

    def load(self):
        """Load samples from a gzipped json file."""
        with gzip.open(self.file_path) as f:
            self.rows = json.load(f)

    def save(self, pre_timeline_format=True):
        """Save samples as a JSON file."""
        data = self.rows
        if pre_timeline_format:
            data = self.pre_timeline_format_rows

        with open(self.file_path, "w") as f:
            json.dump(data, f)

    def insert(
        self,
        mdp_id,
        sequence_number,
        state,
        action,
        reward,
        next_state,
        next_action,
        terminal,
        possible_actions,
        possible_next_actions,
        possible_next_actions_lengths,
        time_diff,
        action_probability,
    ):
        """
        Insert a new sample to the dataset.
        """

        assert isinstance(state, list)
        assert isinstance(action, (list, str))
        assert isinstance(reward, float)
        assert isinstance(next_state, list)
        assert isinstance(next_action, list)
        assert isinstance(terminal, bool)
        assert possible_actions is None or isinstance(
            possible_actions, (list, np.ndarray)
        )
        assert possible_next_actions is None or isinstance(
            possible_next_actions, (list, np.ndarray)
        )
        assert isinstance(possible_next_actions_lengths, int)
        assert isinstance(time_diff, int)
        assert isinstance(action_probability, float)

        self.rows.append(
            {
                "state": state,
                "action": action,
                "reward": reward,
                "next_state": next_state,
                "next_action": next_action,
                "terminal": terminal,
                "possible_next_actions": possible_next_actions,
                "possible_next_actions_lengths": possible_next_actions_lengths,
                "time_diff": time_diff,
            }
        )

        state_features = {int(i): v for i, v in enumerate(state)}

        idx_bump = max(state_features.keys()) + 1
        if isinstance(action, list):
            action = {int(i + idx_bump): v for i, v in enumerate(action)}
        if isinstance(possible_actions, list):
            if len(possible_actions) == 0:
                pass
            elif isinstance(possible_actions[0], int):
                # Discrete action domain
                possible_actions = [
                    idx for idx, val in enumerate(possible_actions) if val == 1
                ]
            elif isinstance(possible_actions[0], dict):
                # Parametric or continuous action domain
                possible_actions = [
                    {int(k + idx_bump): v for v, k in enumerate(action)}
                    for action in possible_actions
                ]

        self.pre_timeline_format_rows.append(
            {
                "ds": "2019-01-01",  # Fix ds for simplicity in open source examples
                "mdp_id": str(mdp_id),
                "sequence_number": int(sequence_number),
                "state_features": {int(i): v for i, v in enumerate(state)},
                "action": action,
                "reward": reward,
                "action_probability": action_probability,
                "possible_actions": possible_actions,
            }
        )

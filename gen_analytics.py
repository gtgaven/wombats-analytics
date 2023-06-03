import sys
import json
from pathlib import Path

from Game import Game
from Season import SeasonStats

SEASONS_TO_REGEN = ['2023']

def main():
    for s in SEASONS_TO_REGEN:
        with open(f'input/{s}/season_config.json', "r") as config:
            json_config = json.load(config)

        season = SeasonStats(json_config)
        season.export_non_cumulative_stats_pretty("non_cumulative_stats.csv")
        season.export_cumulative_stats_pretty("cumulative_stats.csv")

if __name__ == "__main__":
    main()

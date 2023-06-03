import sys
import json
from pathlib import Path

from Game import Game
from Season import SeasonStats

SEASONS_TO_REGEN = ['2022', '2023']

def main():
    for s in SEASONS_TO_REGEN:
        with open(f'input/{s}/season_config.json', "r") as config:
            json_config = json.load(config)

        season = SeasonStats(json_config)
        season.export_non_cumulative_stats_pretty("non_cumulative.csv")
        season.export_cumulative_stats_pretty("cumulative.csv")
        season.export_raw_non_cumulative_data("raw_non_cumulative.csv")
        season.export_raw_cumulative_data("raw_cumulative.csv")
        print(f'Files exported to ./output/{s}/')


if __name__ == "__main__":
    main()

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
        season.export_non_cumulative_stats_pretty("non_cumulative.html")
        season.export_cumulative_stats_pretty("cumulative.html")
        season.export_raw_non_cumulative_data("raw_non_cumulative.csv")
        season.export_raw_cumulative_data("raw_cumulative.csv")
        print(f'Files exported to ./output/{s}/')

    #TODO need to add a test to make sure no regression happens, can use expected 2022 data compared to output

if __name__ == "__main__":
    main()

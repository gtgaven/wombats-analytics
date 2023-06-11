import sys
import json

from Career import CareerStats
from Season import SeasonStats

SEASONS_TO_REGEN = ['2021', '2022', '2023']
ALL_TIME_STATS_FILEPATH = 'output/all_time_stats.csv'
PRETTY_CUMULATIVE_FILENAME = 'cumulative.html'
PRETTY_NON_CUMULATIVE_FILENAME = 'non_cumulative.html'
RAW_CUMULATIVE_FILENAME = 'raw_cumulative.csv'
RAW_NON_CUMULATIVE_FILENAME = 'raw_non_cumulative.csv'

def validate_output():
    expected = ['Zach','14','12','40','16','3','1','0','20','1','3','3','27','36','0.75','0.7','1.1944444444444444\n']
    with open('output/2022/raw_cumulative.csv', "r") as stats_file:
        final_line = stats_file.readlines()[-1]
        last_line_as_list = final_line.split(',')

    if last_line_as_list != expected:
        raise RuntimeError(f'Failed validation, read \n{last_line_as_list}, expected \n{expected}')
    

def main():
    career_stats = CareerStats()
    for s in SEASONS_TO_REGEN:
        with open(f'input/{s}/season_config.json', "r") as config:
            json_config = json.load(config)

        season = SeasonStats(json_config)
        season.export_non_cumulative_stats_pretty(PRETTY_NON_CUMULATIVE_FILENAME)
        season.export_cumulative_stats_pretty(PRETTY_CUMULATIVE_FILENAME)
        season.export_raw_non_cumulative_data(RAW_NON_CUMULATIVE_FILENAME)
        season.export_raw_cumulative_data(RAW_CUMULATIVE_FILENAME)
        print(f'Files exported to ./output/{s}/')

        for player in json_config["roster"]:
            career_stats.add_player_data(player, season.calculate_cumulative_stats_for_player(player, len(season.games)))

    print(f'all time stats exported to {ALL_TIME_STATS_FILEPATH}')
    career_stats.export(ALL_TIME_STATS_FILEPATH)

    validate_output()


if __name__ == "__main__":
    main()

import sys
import argparse
from distutils.dir_util import copy_tree
import json
from utils import export_webapp_landing_pages

from Career import CareerStats
from Season import SeasonStats
from view_analytics import export_all_graphs

SEASONS_TO_REGEN = ['2021', '2022', '2023']
PRETTY_ALL_TIME_STATS_FILEPATH = 'output/webapp/all_time_stats.html'
PRETTY_CUMULATIVE_FILENAME = 'cumulative.html'
PRETTY_NON_CUMULATIVE_FILENAME = 'non_cumulative.html'
RAW_ALL_TIME_STATS_FILEPATH = 'output/raw_all_time_stats.csv'
RAW_CUMULATIVE_FILENAME = 'raw_cumulative.csv'
RAW_NON_CUMULATIVE_FILENAME = 'raw_non_cumulative.csv'
WEBAPP_DIRECTORY = 'output/webapp'

def validate_output():
    expected = ['Zach','14','12','40','16','3','1','0','20','1','3','3','27','36','0.75','0.7','1.1944444444444444\n']
    with open('output/2022/raw_cumulative.csv', "r") as stats_file:
        final_line = stats_file.readlines()[-1]
        last_line_as_list = final_line.split(',')

    if last_line_as_list != expected:
        raise RuntimeError(f'Failed validation, read \n{last_line_as_list}, expected \n{expected}')
    

def main(update_webapp=False):
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

    career_stats.export_raw(RAW_ALL_TIME_STATS_FILEPATH)
    career_stats.export_pretty(PRETTY_ALL_TIME_STATS_FILEPATH)
    validate_output()


    if update_webapp:
        print("Updating webapp files!")
        export_all_graphs(SEASONS_TO_REGEN, 'output/webapp')
        export_webapp_landing_pages('output/webapp', SEASONS_TO_REGEN)
        try:
            copy_tree("css", "output/webapp/css")
            copy_tree("output/webapp", "/opt/tomcat/webapps/wombats/")
        except OSError:
            print(f'failed to copy directory')
    else:
        print("No updating webapp files")




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update_webapp", help="overwrite webapp html files with newly generated files")
    args = parser.parse_args()
    main(args.update_webapp)

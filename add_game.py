import argparse
import csv
import json

from game import Game
from database_connection import DbConnection


def add_game(args):
    game = Game(args.game_json, args.stats_csv)
    print(f'{game} - input validated successfully')

    db = DbConnection('root', 'winnie2', args.commit_changes)
    db.verify_players_exist_in_database(game.player_stats.keys())
    db.insert_game(game)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit_changes", help="actually update the database", default=False)
    parser.add_argument("--game_json", help="path to the game config json file")
    parser.add_argument("--stats_csv", help="path to the stats csv file")
    args = parser.parse_args()

    if args.commit_changes:
        input("Are you sure you want to commit database changes?")

    add_game(args)

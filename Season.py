import csv
import os
from pathlib import Path

from utils import format_float

from Game import Game
from Player import PlayerStats

class SeasonStats:

    def __init__(self, cfg):
        self.cfg = cfg
        self.games = []
        for i, json in enumerate(cfg["games"]):
            self.add_game(Game(i+1, json, cfg["roster"], f'input/{cfg["year"]}'))

        for g in self.games:
            g.load_stats()


    def add_game(self, game):
        self.games.append(game)

        
    def calculate_cumulative_stats_for_player(self, player_name, num_games_to_accumulate):
        cumulative_player_stats = PlayerStats()
        for i, s in enumerate(self.games):
            if i >= num_games_to_accumulate:
                break

            cumulative_player_stats += s.player_stats[player_name]


        return cumulative_player_stats

    def export_cumulative_stats_pretty(self, output_file_name):
        #todo convert to better looking format. html?
        export_path = f'output/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:
            out_file.write('Player,GP,PA,R,SF,BB,K,1B,2B,3B,HR,H,AB,AVG,OBP,SLG\n')
            for p in self.cfg["roster"]:
                s = self.calculate_cumulative_stats_for_player(p, len(self.games))
                out_file.write(f'{p},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{s.hits()},{s.at_bats()},{format_float(s.avg())},{format_float(s.obp())},{format_float(s.slg())}\n')

    def export_non_cumulative_stats_pretty(self, output_file_name):
        #todo convert to better looking format. html?
        export_path = f'output/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:

            for g in self.games:
                out_file.write(f'Game {g.game_num}\n')
                if g.was_home:
                    out_file.write(f' vs {g.op}\n')
                else:
                    out_file.write(f' @ {g.op}\n')
                
                if g.op_score < g.score:
                    out_file.write(f' Win - {g.score} to {g.op_score}\n')
                elif g.op_score > g.score:
                    out_file.write(f' Loss - {g.op_score} to {g.score}\n')
                else:
                    out_file.write(f' Tie - {g.score} to {g.op_score}\n')

                out_file.write('Player,PA,R,SF,BB,K,1B,2B,3B,HR,H,AB,AVG,OBP,SLG\n')
                for p in sorted(g.roster):
                    s = g.player_stats[p]
                    out_file.write(f'{p},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{s.hits()},{s.at_bats()},{format_float(s.avg())},{format_float(s.obp())},{format_float(s.slg())}\n')


    def export_raw_cumulative_data(self, output_file_name):
        export_path = f'output/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:
            out_file.write('Player,GP,PA,R,SF,BB,K,1B,2B,3B,HR,Game\n')
            for i, s in enumerate(self.games):
                for p in self.cfg["roster"]:
                    s = self.calculate_cumulative_stats_for_player(p, i+1)
                    out_file.write(f'{p},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{i+1}\n')


    def export_raw_non_cumulative_data(self, output_file_name):
        export_path = f'output/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:
            out_file.write('Player,GP,PA,R,SF,BB,K,1B,2B,3B,HR,Game,Home,Opponent,Op. Score\n')
            for i, g in enumerate(self.games):
                for p in sorted(g.roster):
                    s = g.player_stats[p]
                    out_file.write(f'{p},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{i+1},{g.was_home},{g.op},{g.op_score}\n')

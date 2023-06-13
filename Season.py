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
        # TODO is html the best way to output this..?
        export_path = f'output/webapp/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:
            out_file.write('<!DOCTYPE html><html><head><link rel="stylesheet" href="../css/styles.css"></head>')
            out_file.write(f'''<body><div>
                <table>
                <caption>Wombats {self.cfg["year"]}</caption>
                <thead>
                    <tr>
                    <th>Player</th>
                    <th>GP</th>
                    <th>PA</th>
                    <th>R</th>
                    <th>SF</th>
                    <th>BB</th>
                    <th>K</th>
                    <th>1B</th>
                    <th>2B</th>
                    <th>3B</th>
                    <th>HR</th>
                    <th>H</th>
                    <th>AB</th>
                    <th>AVG</th>
                    <th>OBP</th>
                    <th>SLG</th>
                    </tr>
                </thead><tbody>''')
            for p in self.cfg["roster"]:
                s = self.calculate_cumulative_stats_for_player(p, len(self.games))
                out_file.write(f'''<tr>
                <td align="left">{p}</td>
                <td>{s.games_played}</td>
                <td>{s.plate_appearances}</td>
                <td>{s.runs}</td>
                <td>{s.sac_flies}</td>
                <td>{s.walks}</td>
                <td>{s.strikeouts}</td>
                <td>{s.singles}</td>
                <td>{s.doubles}</td>
                <td>{s.triples}</td>
                <td>{s.home_runs}</td>
                <td>{s.hits()}</td>
                <td>{s.at_bats()}</td>
                <td>{format_float(s.avg())}</td>
                <td>{format_float(s.obp())}</td>
                <td>{format_float(s.slg())}</td>
                </tr>''')

            out_file.write('</tbody></table></div></body></html>')


    def export_non_cumulative_stats_pretty(self, output_file_name):
        # TODO is html the best way to output this..?
        export_path = f'output/webapp/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:

            out_file.write('<!DOCTYPE html><html><head><link rel="stylesheet" href="../css/styles.css"></head>')
            out_file.write('<body><div>')

            for g in self.games:
                preposition_str = 'vs' if g.was_home else '@'
                win_loss_str = f'W ({g.score} to {g.op_score})' if g.op_score < g.score else f'L ({g.op_score} to {g.score})'
                out_file.write(f'''
                    <table>
                    <caption>Wombats {self.cfg["year"]} Game {g.game_num} {preposition_str} {g.op} - {win_loss_str}</caption>
                    <thead>
                        <tr>
                        <th>Player</th>
                        <th>PA</th>
                        <th>R</th>
                        <th>SF</th>
                        <th>BB</th>
                        <th>K</th>
                        <th>1B</th>
                        <th>2B</th>
                        <th>3B</th>
                        <th>HR</th>
                        <th>H</th>
                        <th>AB</th>
                        <th>AVG</th>
                        <th>OBP</th>
                        <th>SLG</th>
                        </tr>
                    </thead><tbody>''')
                for p in sorted(g.roster):
                    s = g.player_stats[p]
                    out_file.write(f'''<tr>
                        <td align="left">{p}</td>
                        <td>{s.plate_appearances}</td>
                        <td>{s.runs}</td>
                        <td>{s.sac_flies}</td>
                        <td>{s.walks}</td>
                        <td>{s.strikeouts}</td>
                        <td>{s.singles}</td>
                        <td>{s.doubles}</td>
                        <td>{s.triples}</td>
                        <td>{s.home_runs}</td>
                        <td>{s.hits()}</td>
                        <td>{s.at_bats()}</td>
                        <td>{format_float(s.avg())}</td>
                        <td>{format_float(s.obp())}</td>
                        <td>{format_float(s.slg())}</td></tr>''')
            
                out_file.write('</tbody></table><hr>')
            out_file.write('</div></body></html>')

    def export_raw_cumulative_data(self, output_file_name):
        export_path = f'output/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:
            out_file.write('Player,Game,GP,PA,R,SF,BB,K,1B,2B,3B,HR,H,AB,AVG,OBP,SLG\n')
            for i, s in enumerate(self.games):
                for p in self.cfg["roster"]:
                    s = self.calculate_cumulative_stats_for_player(p, i+1)
                    out_file.write(f'{p},{i+1},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{s.hits()},{s.at_bats()},{s.avg()},{s.obp()},{s.slg()}\n')


    def export_raw_non_cumulative_data(self, output_file_name):
        export_path = f'output/{self.cfg["year"]}/{output_file_name}'
        Path(os.path.dirname(export_path)).mkdir(parents=True, exist_ok=True)
        with open(export_path, "w") as out_file:
            out_file.write('Player,Game,GP,PA,R,SF,BB,K,1B,2B,3B,HR,H,AB,AVG,OBP,SLG,Home,Opponent,Op. Score\n')
            for i, g in enumerate(self.games):
                for p in sorted(g.roster):
                    s = g.player_stats[p]
                    out_file.write(f'{p},{i+1},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{s.hits()},{s.at_bats()},{s.avg()},{s.obp()},{s.slg()},{g.was_home},{g.op},{g.op_score}\n')

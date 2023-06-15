import collections
import os
from pathlib import Path

from Player import PlayerStats
from utils import format_float

class CareerStats:
    def __init__(self):
        self.all_players = dict()

    def add_player_data(self, player_name, player_stats: PlayerStats):
        if player_name in self.all_players:
            updated_stats = self.all_players[player_name] + player_stats
            self.all_players[player_name] = updated_stats
        else:
            self.all_players[player_name] = player_stats

    def export_pretty(self, export_file_path):
        sorted_player_stats = collections.OrderedDict(sorted(self.all_players.items()))
        Path(os.path.dirname(export_file_path)).mkdir(parents=True, exist_ok=True)
        with open(export_file_path, "w") as out_file:
            out_file.write(f'''<!DOCTYPE html><html><head><link rel="stylesheet" href="../css/styles.css"></head><body><div>
                                <table>
                                <caption>West Building Wombats</caption>
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
            for p, s in sorted_player_stats.items():
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

    def export_raw(self, export_file_path):
        with open(export_file_path, "w") as out_file:
            out_file.write('Player,GP,PA,R,SF,BB,K,1B,2B,3B,HR,H,AB,AVG,OBP,SLG\n')
            sorted_player_stats = collections.OrderedDict(sorted(self.all_players.items()))
            for p, s in sorted_player_stats.items():
                out_file.write(f'{p},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{s.hits()},{s.at_bats()},{s.avg()},{s.obp()},{s.slg()}\n')

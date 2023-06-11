import collections

from Player import PlayerStats

class CareerStats:
    def __init__(self):
        self.all_players = dict()

    def add_player_data(self, player_name, player_stats: PlayerStats):
        if player_name in self.all_players:
            updated_stats = self.all_players[player_name] + player_stats
            self.all_players[player_name] = updated_stats
        else:
            self.all_players[player_name] = player_stats

    def export(self, export_file_path):
        with open(export_file_path, "w") as out_file:
            out_file.write('Player,GP,PA,R,SF,BB,K,1B,2B,3B,HR,H,AB,AVG,OBP,SLG\n')
            sorted_player_stats = collections.OrderedDict(sorted(self.all_players.items()))
            for p, s in sorted_player_stats.items():
                out_file.write(f'{p},{s.games_played},{s.plate_appearances},{s.runs},{s.sac_flies},{s.walks},{s.strikeouts},{s.singles},{s.doubles},{s.triples},{s.home_runs},{s.hits()},{s.at_bats()},{s.avg()},{s.obp()},{s.slg()}\n')

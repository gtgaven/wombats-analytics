import csv
from pathlib import Path
from Player import PlayerStats

class Game:
    def __init__(self, game_num: int, game_json, roster, input_dir: str):
        self.game_num = game_num
        self.input_dir = input_dir
        self.roster = set(roster)
        self.was_home = game_json["was_home"]
        self.op = game_json["op"]
        self.op_score = game_json["op_score"]
        self.score = game_json["score"]
        self.player_count = game_json["player_count"]
        self.player_stats_file_name = f'game_{self.game_num}.csv'
        self.player_stats = dict()


    def load_stats(self):
        with open(Path(self.input_dir, self.player_stats_file_name), "r") as stats_file:
            reader = csv.reader(stats_file)
            header = next(reader)
            if header != PlayerStats.EXPECTED_FORMAT:
                raise RuntimeError("invalid header format")

            absent_players = self.roster.copy()

            for row in reader:
                if (row[0] not in absent_players):
                    raise RuntimeError(f'{row[0]} is not in the roster or appears twice in the stats')
                absent_players.remove(row[0])
                self.player_stats[row[0]] = PlayerStats(int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]), int(row[8]), int(row[9]))

            if len(absent_players) != (len(self.roster) - self.player_count):
                raise RuntimeError(f'mismatch between absent players and player count')

            for absent_player in absent_players:
                self.player_stats[absent_player] = PlayerStats()

        self.__validate()


    def __validate(self):
        calculated_score = 0
        calculated_player_count = 0
        for name in self.roster:
            calculated_score += self.player_stats[name].runs

        if calculated_score != self.score:
            raise RuntimeError(f'calculated score ({calculated_score}) does not match scorebook ({self.score})')

        if len(self.player_stats) != len(self.roster):
            raise RuntimeError(f'expected {len(self.roster)} player stats. created {len(self.player_stats)}')

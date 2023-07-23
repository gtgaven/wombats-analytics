import csv
import json
from pathlib import Path
from player import PlayerStats

ROSTERS = {
    "2021": ["Anna",
            "Brad",
            "Brandon",
            "Carol",
            "Greg",
            "Isaac",
            "Jake",
            "Jamila",
            "Katie",
            "Lance",
            "Nate La",
            "Phil",
            "Ruthie",
            "Ryan",
            "Ted",
            "Walt"]}

class Game:
    def __init__(self, game_json_path, stats_csv_path):
        with open(game_json_path, "r") as config:
            game_json = json.load(config)

        self.year = game_json["year"]
        self.team = game_json["team"]
        self.gamenum = game_json["game_num"]
        self.roster = set(ROSTERS[str(self.year)])
        self.was_home = game_json["was_home"]
        self.opponent = game_json["op"]
        self.opponentscore = game_json["op_score"]
        self.score = game_json["score"]
        self.player_count = game_json["player_count"]
        self.player_stats = dict()
        self._load_stats(stats_csv_path)

    def __str__(self):
        return f'{self.year} {self.team} #{self.gamenum} vs {self.opponent}'

    def _load_stats(self, stats_csv_path):
        with open(stats_csv_path, "r") as stats_file:
            reader = csv.reader(stats_file)
            header = next(reader)
            if header != PlayerStats.EXPECTED_FORMAT:
                raise RuntimeError("invalid header format")

            absent_players = self.roster.copy()

            for row in reader:
                if (row[0] not in absent_players):
                    raise RuntimeError(f'{row[0]} is not in the roster or appears twice in the stats')
                absent_players.remove(row[0])
                self.player_stats[row[0]] = PlayerStats(1, int(row[1]), int(row[2]), int(row[3]), int(row[4]), int(row[5]), int(row[6]), int(row[7]), int(row[8]), int(row[9]))

            if len(absent_players) != (len(self.roster) - self.player_count):
                raise RuntimeError(f'mismatch between absent players and player count')

            for absent_player in absent_players:
                self.player_stats[absent_player] = PlayerStats()

        self._validate()

    def _validate(self):
        calculated_score = 0
        for name in self.roster:
            calculated_score += self.player_stats[name].runs

        if calculated_score != self.score:
            raise RuntimeError(f'calculated score ({calculated_score}) does not match scorebook ({self.score})')

        if len(self.player_stats) != len(self.roster):
            raise RuntimeError(f'expected {len(self.roster)} player stats. created {len(self.player_stats)}')

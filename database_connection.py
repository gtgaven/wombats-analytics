from mysql import connector

class DbConnection():
    def __init__(self, username, password, commit_changes=False):
        self.db = connector.connect(host='localhost', database='softball', user=username, password=password)
        self.commit_changes = commit_changes
        self.cursor = self.db.cursor()

    def _execute_command(self, command):
        if self.commit_changes:
            self.cursor.execute(command)
            self.db.commit()
        else:
            print(f"DRYRUN: would have executed {command}")

    def _insert_player_stat(self, player_id, game_id, stat):
        insert_command = f'''INSERT INTO playerstat (player, 
                                                     game, 
                                                     plateappearances,
                                                     runs,
                                                     sacflies,
                                                     walks,
                                                     strikeouts,
                                                     singles,
                                                     doubles,
                                                     triples,
                                                     homeruns)
                             VALUES ({player_id}, 
                                     {game_id},
                                     {stat.plate_appearances},
                                     {stat.runs},
                                     {stat.sac_flies},
                                     {stat.walks},
                                     {stat.strikeouts},
                                     {stat.singles},
                                     {stat.doubles},
                                     {stat.triples},
                                     {stat.home_runs});'''
        self._execute_command(insert_command)

    def _insert_player_stats(self, game):
        game_id = self.get_game_id(game.team, game.year, game.gamenum)
        for player, stat in game.player_stats.items():
            if stat.games_played != 1:
                continue

            player_id = self.get_player_id(player)
            self._insert_player_stat(player_id, game_id, stat)

    def get_game_id(self, team, year, gamenum):
        self.cursor.execute(f'SELECT id, team, year, gamenum FROM game WHERE team = "{team}" AND year = {year} AND gamenum = {gamenum};')
        games = self.cursor.fetchall()
        if len(games) > 1:
            raise RuntimeError(f'multiple games returned for {team}, {year}, #{gamenum}')

        if len(games) == 0:
            return 0

        return games[0][0]

    def get_player_id(self, playername):
        self.cursor.execute(f'SELECT id FROM player WHERE name="{playername}";')
        ids = self.cursor.fetchall()
        if len(ids) != 1:
            raise RuntimeError(f'player with name {playername} not found in DB, len {len(ids)}')
        
        return ids[0][0]

    def insert_game(self, game):
        if self.get_game_id(game.team, game.year, game.gamenum) != 0:
            raise RuntimeError(f'Game already exists in database - {game}')

        insert_command = f'''INSERT INTO game (year,
                                               team,
                                               gamenum,
                                               opponent,
                                               opponentscore,
                                               washome)
                             VALUES ({game.year},
                                     "{game.team}",
                                     {game.gamenum},
                                     "{game.opponent}",
                                     {game.opponentscore},
                                     {game.was_home});'''
        self._execute_command(insert_command)
        self._insert_player_stats(game)

    def insert_player(self, player_name):
        self._execute_command(f'INSERT INTO player (name) VALUES ("{player_name}");')

    def verify_players_exist_in_database(self, players):
        for player in players:
            id = self.get_player_id(player)
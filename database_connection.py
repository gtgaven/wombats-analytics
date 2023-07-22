import threading
from mysql import connector
from player import PlayerStats

PLAYER_COLUMNS = "plateappearances, runs, sacflies, walks, strikeouts, singles, doubles, triples, homeruns"

class DbConnection():

    _db_lock = threading.Lock()

    def __init__(self, username, password, commit_changes=False):
        self.db = connector.connect(host='localhost', database='softball', user=username, password=password)
        self.commit_changes = commit_changes
        self.cursor = self.db.cursor()

    def _execute_command(self, command):
        DbConnection._db_lock.acquire()
        try:
            if self.commit_changes:
                self.cursor.execute(command)
                self.db.commit()
            else:
                print(f"DRYRUN: would have executed {command}")
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

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

    def get_stats_for_player_in_seasons(self, playername, seasons):
        and_str = ''
        for i, s in enumerate(seasons):
            if i == len(seasons)-1:
                and_str += f'game.year={s}'
            else:
                and_str += f'game.year={s} OR '
        and_str +=');'

        id = self.get_player_id(playername)
        query = f'''SELECT * FROM playerstat
                    INNER JOIN game ON playerstat.game=game.id
                    WHERE playerstat.player={id} AND ('''
        query += and_str
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(query)
            query_results = self.cursor.fetchall()
        except Exception as e:
            raise e 
        finally:
            DbConnection._db_lock.release()

        print(query_results)

        stats = PlayerStats()
        for p in query_results:
            stats = stats + PlayerStats(1, p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11])

        return stats

    def get_career_stats_for_player(self, playername):
        return self.get_stats_for_player_in_seasons(playername, self.get_seasons())

    def get_all_stats(self):
        DbConnection._db_lock.acquire()
        query = f'''SELECT * FROM playerstat
                    INNER JOIN game ON playerstat.game=game.id
                    INNER JOIN player ON playerstat.player=player.id;'''
        self.cursor.execute(query)
        playerstats = self.cursor.fetchall()
        return playerstats

    def get_game_id(self, team, year, gamenum):
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(f'SELECT id, team, year, gamenum FROM game WHERE team = "{team}" AND year = {year} AND gamenum = {gamenum};')
            games = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        if len(games) > 1:
            raise RuntimeError(f'multiple games returned for {team}, {year}, #{gamenum}')

        if len(games) == 0:
            return 0

        return games[0][0]

    def get_player_id(self, playername):
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(f'SELECT id FROM player WHERE name="{playername}";')
            ids = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        if len(ids) != 1:
                raise RuntimeError(f'player with name {playername} not found in DB, len {len(ids)}')
        return ids[0][0]

    def get_player_list(self):
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute('SELECT name FROM player;')
            query_result = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        names = [n[0] for n in query_result]
        return names

    def get_player_list_for_season(self, season):
        if season == 'All':
            return self.get_player_list()
        
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(f'''SELECT player, name FROM playerstat 
                                    INNER JOIN game ON playerstat.game=game.id
                                    INNER JOIN player ON playerstat.player=player.id
                                    WHERE game.year={season};''')
            query_result = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        names = [n[1] for n in query_result]
        return names

    def get_seasons(self):
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute('SELECT DISTINCT year FROM game;')
            query_result = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        seasons = [n[0] for n in query_result]
        return seasons

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

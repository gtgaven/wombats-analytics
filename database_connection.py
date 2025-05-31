import threading
import json
from mysql import connector
from player import PlayerStats


class DbConnection():

    _db_lock = threading.Lock()
    DB_CONFIG_FILENAME = "config/.db.json"
    DB_HOSTNAME = "unknown"
    DB_DATABASE = "unknown"
    DB_USERNAME = "unknown"
    DB_PASSWORD = "unknown"

    try:
        with open(DB_CONFIG_FILENAME) as cfg:
            db_config = json.load(cfg)
            DB_HOSTNAME = db_config["host"]
            DB_DATABASE = db_config["database"]
            DB_USERNAME = db_config["username"]
            DB_PASSWORD = db_config["password"]
    except Exception as e:
        raise RuntimeError(f"failed to read db config file {DB_CONFIG_FILENAME=}, reason {e}")

    def __init__(self, commit_changes=False):

        self.db = connector.connect(host=DbConnection.DB_HOSTNAME, database=DbConnection.DB_DATABASE, user=DbConnection.DB_USERNAME, password=DbConnection.DB_PASSWORD)
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

    def get_game_ids_in_season(self, year):
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(f'SELECT id FROM game WHERE year={year};')
            game_ids = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        return [i[0] for i in game_ids]

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

    def get_raw_stats_from_game_id(self, game_id):
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(f'SELECT gamenum, opponent, washome FROM game WHERE id={game_id};')
            results = self.cursor.fetchall()
            game_num = results[0][0]
            opponent = results[0][1]
            was_home = results[0][2]
            
            self.cursor.execute(f'''SELECT name, plateappearances, runs, sacflies, walks, strikeouts, singles, doubles, triples, homeruns 
                                    FROM playerstat
                                    INNER JOIN game ON playerstat.game=game.id
                                    INNER JOIN player ON playerstat.player=player.id
                                    WHERE playerstat.game={game_id};''')
            game_stats = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        return {'game_num': game_num, 'opponent': opponent, 'was_home': was_home, 'stats': game_stats}

    def get_roster_for_season(self, season):
        if season == 'All':
            return self.get_player_list()

        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(f'''SELECT player, name FROM roster
                                    INNER JOIN player ON roster.player=player.id
                                    WHERE roster.year={season};''')
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
            self.cursor.execute('SELECT DISTINCT year FROM roster;')
            query_result = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        seasons = [n[0] for n in query_result]
        return seasons

    def get_cumulative_stats(self, player, season):
        players = []
        if season == 'All':
            seasons = self.get_seasons()
            players = self.get_player_list()
        else:
            seasons = [season]
            players = self.get_roster_for_season(season)

        if player in players:
            return self.get_stats_for_player_in_seasons(player, seasons)

        player_cumulative_stats = []
        team_cumulative_stats = PlayerStats()
        for p in players:
            stats = self.get_stats_for_player_in_seasons(p, seasons)
            player_cumulative_stats.append(stats)
            team_cumulative_stats += stats
        
        if player == 'Team Cumulative':
            return team_cumulative_stats
        elif player == 'Mean Wombat':
            return PlayerStats(round(team_cumulative_stats.games_played/len(players), 2),
                            round(team_cumulative_stats.plate_appearances/len(players), 2),
                            round(team_cumulative_stats.runs/len(players), 2),
                            round(team_cumulative_stats.sac_flies/len(players), 2),
                            round(team_cumulative_stats.walks/len(players), 2),
                            round(team_cumulative_stats.strikeouts/len(players), 2),
                            round(team_cumulative_stats.singles/len(players), 2),
                            round(team_cumulative_stats.doubles/len(players), 2),
                            round(team_cumulative_stats.triples/len(players), 2),
                            round(team_cumulative_stats.home_runs/len(players), 2))
        elif player == 'Median Wombat':
            middle_index = int(len(player_cumulative_stats) / 2) - 1
            return PlayerStats(sorted(player_cumulative_stats, key=lambda x: x.games_played)[middle_index].games_played,
                            sorted(player_cumulative_stats, key=lambda x: x.plate_appearances)[middle_index].plate_appearances,
                            sorted(player_cumulative_stats, key=lambda x: x.runs)[middle_index].runs,
                            sorted(player_cumulative_stats, key=lambda x: x.sac_flies)[middle_index].sac_flies,
                            sorted(player_cumulative_stats, key=lambda x: x.walks)[middle_index].walks,
                            sorted(player_cumulative_stats, key=lambda x: x.strikeouts)[middle_index].strikeouts,
                            sorted(player_cumulative_stats, key=lambda x: x.singles)[middle_index].singles,
                            sorted(player_cumulative_stats, key=lambda x: x.doubles)[middle_index].doubles,
                            sorted(player_cumulative_stats, key=lambda x: x.triples)[middle_index].triples,
                            sorted(player_cumulative_stats, key=lambda x: x.home_runs)[middle_index].home_runs)

        raise RuntimeError(f'unknown player {player}')

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

    def insert_roster_item(self, year, player_name):
        pid = self.get_player_id(player_name)
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(f'SELECT player FROM roster WHERE player={pid} AND year={year};')
            players = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()

        if len(players) != 0:
                raise RuntimeError(f'{player_name} already exists in roster for year {year}')

        self._execute_command(f'INSERT INTO roster (player, year) VALUES ({pid}, {year});')

    def verify_players_exist_in_database(self, players):
        for player in players:
            id = self.get_player_id(player)

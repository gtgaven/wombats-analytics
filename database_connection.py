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

    def _execute_query(self, query):
        DbConnection._db_lock.acquire()
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
        except Exception as e:
            raise e
        finally:
            DbConnection._db_lock.release()
        return results

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

    def get_stats_for_player_in_seasons(self, playername, seasons) -> PlayerStats:
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
        query_results = self._execute_query(query)
            
        stats = PlayerStats()
        for p in query_results:
            stats = stats + PlayerStats(1, p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11])

        return stats

    def get_all_player_stats_for_player(self, playername):
        id = self.get_player_id(playername)
        query = f'''SELECT game.id, year, plateappearances, runs, sacflies, walks, strikeouts, singles, doubles, triples, homeruns 
                    FROM playerstat
                    INNER JOIN game ON playerstat.game=game.id
                    WHERE playerstat.player={id}'''
        results = self._execute_query(query)
        return ("game_num", "Season", "plate_appearances", "runs", 'sac_flies', 'walks','strikeouts', 'singles', 'doubles', "triples", "home_runs"), results


    def get_career_stats_for_player(self, playername):
        return self.get_stats_for_player_in_seasons(playername, self.get_seasons())

    def get_all_stats(self):
        query = f'''SELECT * FROM playerstat
                    INNER JOIN game ON playerstat.game=game.id
                    INNER JOIN player ON playerstat.player=player.id;'''
        
        playerstats = self._execute_query(query)
        return playerstats

    def get_game_id(self, team, year, gamenum):
        games = self._execute_query(f'SELECT id, team, year, gamenum FROM game WHERE team = "{team}" AND year = {year} AND gamenum = {gamenum};')

        if len(games) > 1:
            raise RuntimeError(f'multiple games returned for {team}, {year}, #{gamenum}')

        if len(games) == 0:
            return 0

        return games[0][0]

    def get_game_ids_in_season(self, year):
        if year == "All":
            game_ids = self._execute_query(f'SELECT id FROM game;')
        else:
            game_ids = self._execute_query(f'SELECT id FROM game WHERE year={year};')

        return [i[0] for i in game_ids]

    def get_num_games(self, year, home):
        if home == "Any":
            if year == "All":
                count = self._execute_query(f'SELECT COUNT(id) FROM game;')
            else:
                count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE year={year};')

            return count[0][0]

        if home:
            return self._get_num_home_games(year)
        else:
            return self._get_num_away_games(year)


    def _get_num_home_games(self, year):
        if year == "All":
            count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE washome=1;')
        else:
            count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE year={year} and washome=1;')

        return count[0][0]

    def _get_num_away_games(self, year):
        if year == "All":
            count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE washome=0;')
        else:
            count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE year={year} and washome=0;')

        return count[0][0]

    def get_wins_in_year(self, year: int | str, home: bool | str):
        if year == "All":
            if home == "Any":
                count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE score > opponentscore;')
            elif home:
                count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE score > opponentscore AND washome=1;')
            else:
                count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE score > opponentscore AND washome=0;')
        else:
            if home == "Any":
                count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE score > opponentscore AND year={year};')
            elif home:
                count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE score > opponentscore AND year={year} AND washome=1;')
            else:
                count = self._execute_query(f'SELECT COUNT(id) FROM game WHERE score > opponentscore AND year={year} AND washome=0;')

        return count[0][0]

    def get_runs_in_year(self, own: bool, year: int | str, home: bool | str):
        if own:
            table_field = "score"
        else:
            table_field = "opponentscore"

        if year == "All":
            return self._get_runs_all_time(table_field, home)
        else:
            return self._get_runs_in_year(table_field, home, year)

    def _get_runs_all_time(self, table_field: str, home: bool | str):
        if home == "Any":
            count = self._execute_query(f'SELECT SUM({table_field}) FROM game;')
        elif home:
            count = self._execute_query(f'SELECT SUM({table_field}) FROM game where washome=1;')
        else:
            count = self._execute_query(f'SELECT SUM({table_field}) FROM game where washome=0;')

        return count[0][0]

    def _get_runs_in_year(self, table_field: str, home: bool | str, year: int):
        if home == "Any":
            count = self._execute_query(f'SELECT SUM({table_field}) FROM game where year={year};')
        elif home:
            count = self._execute_query(f'SELECT SUM({table_field}) FROM game WHERE year={year} and washome=1;')
        else:
            count = self._execute_query(f'SELECT SUM({table_field}) FROM game WHERE year={year} and washome=0;')

        return count[0][0]

    def get_player_id(self, playername):
        ids = self._execute_query(f'SELECT id FROM player WHERE name="{playername}";')
        if len(ids) != 1:
                raise RuntimeError(f'player with name {playername} not found in DB, len {len(ids)}')
        return ids[0][0]

    def get_player_list(self):
        query_result = self._execute_query('SELECT name FROM player;')

        names = [n[0] for n in query_result]
        return names

    def get_raw_stats_from_game_id(self, game_id):
        results = self._execute_query(f'SELECT gamenum, opponent, opponentscore, washome FROM game WHERE id={game_id};')
        game_num = results[0][0]
        opponent = results[0][1]
        opponentscore = results[0][2]
        was_home = results[0][3]
        
        game_stats = self._execute_query(f'''SELECT name, plateappearances, runs, sacflies, walks, strikeouts, singles, doubles, triples, homeruns 
                                FROM playerstat
                                INNER JOIN game ON playerstat.game=game.id
                                INNER JOIN player ON playerstat.player=player.id
                                WHERE playerstat.game={game_id};''')

        return {'game_num': game_num, 'opponent': opponent, 'opponentscore': opponentscore, 'was_home': was_home, 'stats': game_stats}

    def get_roster_for_season(self, season):
        if season == 'All':
            return self.get_player_list()

        results = self._execute_query(f'''SELECT player, name FROM roster
                                INNER JOIN player ON roster.player=player.id
                                WHERE roster.year={season};''')

        names = [n[1] for n in results]
        return names

    def get_seasons(self):
        results = self._execute_query('SELECT DISTINCT year FROM roster;')

        seasons = [n[0] for n in results]
        return seasons

    def get_player_seasons(self, player):   
        id = self.get_player_id(player)
        results = self._execute_query(f'SELECT year FROM roster WHERE player={id};')

        return [n[0] for n in results]


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
        
        if player == 'Cumulative':
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
                                               washome,
                                               score)
                             VALUES ({game.year},
                                     "{game.team}",
                                     {game.gamenum},
                                     "{game.opponent}",
                                     {game.opponentscore},
                                     {game.was_home},
                                     {game.score});'''
        self._execute_command(insert_command)
        self._insert_player_stats(game)

    def insert_player(self, player_name):
        self._execute_command(f'INSERT INTO player (name) VALUES ("{player_name}");')

    def insert_roster_item(self, year, player_name):
        pid = self.get_player_id(player_name)
        players = self._execute_query(f'SELECT player FROM roster WHERE player={pid} AND year={year};')

        if len(players) != 0:
            raise RuntimeError(f'{player_name} already exists in roster for year {year}')

        self._execute_command(f'INSERT INTO roster (player, year) VALUES ({pid}, {year});')

    def verify_players_exist_in_database(self, players):
        for player in players:
            id = self.get_player_id(player)

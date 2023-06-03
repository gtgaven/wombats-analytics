class PlayerStats:

    # S,D,T are used for single, double triple instead of 1B, 2B and 3B
    # to make data entry easier (entering '1' would autofill to '1B' etc)
    EXPECTED_FORMAT = ['Player', 'PA', 'R', 'SF', 'BB', 'K', 'S', 'D', 'T', 'HR']

    def __init__(self,
                 games_played: int = 0,
                 plate_appearances: int = 0,
                 runs: int = 0,
                 sac_flies: int = 0,
                 walks: int = 0,
                 strikeouts: int = 0,
                 singles: int = 0,
                 doubles: int = 0,
                 triples: int = 0,
                 home_runs: int = 0):
        self.games_played = games_played
        self.plate_appearances = plate_appearances
        self.runs = runs
        self.sac_flies = sac_flies
        self.walks = walks
        self.strikeouts = strikeouts
        self.singles = singles
        self.doubles = doubles
        self.triples = triples
        self.home_runs = home_runs


    def __add__(self, other):
        return PlayerStats(self.games_played + other.games_played,
                           self.plate_appearances + other.plate_appearances,
                           self.runs + other.runs,
                           self.sac_flies + other.sac_flies,
                           self.walks + other.walks,
                           self.strikeouts + other.strikeouts,
                           self.singles + other.singles,
                           self.doubles + other.doubles,
                           self.triples + other.triples,
                           self.home_runs + other.home_runs)


    def at_bats(self):
        if (self.sac_flies + self.walks > self.plate_appearances):
            raise RuntimeError("at bat underflow")

        return self.plate_appearances - self.sac_flies - self.walks


    def avg(self) -> float:
        if (self.at_bats() < self.hits()):
            raise RuntimeError("at bat overflow")

        if self.at_bats() == 0:
            return 0.0

        return self.hits() / self.at_bats()


    def hits(self):
        return self.singles + self.doubles + self.triples + self.home_runs


    def obp(self) -> float:
        ab_bb_sf = self.at_bats() + self.walks + self.sac_flies
        if ab_bb_sf == 0:
            return 0.0

        return (self.hits() + self.walks) / ab_bb_sf


    def slg(self) -> float:
        if self.at_bats() == 0:
            return 0.0

        return (self.singles + (2 * self.doubles) + (3 * self.triples) + 4 * self.home_runs) / self.at_bats()

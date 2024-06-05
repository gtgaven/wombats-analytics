from database_connection import DbConnection

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
            "Walt"],
    "2022": ["Brandon",
            "Carol",
            "Chad",
            "Greg",
            "Hunter",
            "Ian",
            "Josh",
            "Lance",
            "Luke",
            "Matthew",
            "Nate Lo",
            "Phil",
            "Ryan",
            "Shane",
            "Ted",
            "Walt",
            "Zach"],
    "2023": ["Brandon",
            "Cam",
            "Carol",
            "Chad",
            "Greg",
            "Hunter",
            "Ian",
            "Josh",
            "Luke",
            "Moises",
            "Nate Lo",
            "Nate Ly",
            "Paul",
            "Phil",
            "Ryan",
            "Ron",
            "Shane",
            "Steve",
            "Ted",
            "Zach"
        ]
}

def add_roster(year):
    db = DbConnection('root', 'winnie2', False)
    db.verify_players_exist_in_database(ROSTERS[str(year)])
    for p in ROSTERS[str(year)]:
        print(f'adding {p} to {year} roster')
        db.insert_roster_item(year, p)

if __name__ == '__main__':
    add_roster(2021)
    add_roster(2022)
    add_roster(2023)

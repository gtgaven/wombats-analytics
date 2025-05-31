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
        ],
    "2024": ["Carol",
            "Chad",
            "Fahad",
            "Greg",
            "Hunter",
            "Ian",
            "Jack",
            "James",
            "Justin",
            "Keith",
            "Lamo",
            "Nate Lo",
            "Phil",
            "Ron",
            "Ryan",
            "Shane",
            "Steve",
            "Ted",
            "Zach"
        ]
}

def add_roster(year):
    db = DbConnection(False)#change to true if running for real
    db.verify_players_exist_in_database(ROSTERS[str(year)])
    for p in ROSTERS[str(year)]:
        print(f'adding {p} to {year} roster')
        db.insert_roster_item(year, p)


def add_new_player(player_name):
    db = DbConnection(False)#change to true if running for real
    db.insert_player(player_name)

if __name__ == '__main__':
    pass
    #add_roster(2021)
    #add_roster(2022)
    #add_roster(2023)
    #for p in ["Fahad", "Jack", "James", "Justin", "Keith", "Lamo", "Michael"]:
        #add_new_player(p)

    #add_roster(2024)

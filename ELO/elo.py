"""
ELO class based off: 
    https://github.com/ddm7018/Elo/blob/master/elosports/elo.py
FORMULAS found on wiki:
    https://en.wikipedia.org/wiki/Elo_rating_system
"""
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import logging

logging.basicConfig(
    filename="elo.log",
    level=logging.INFO,
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Elo:
    def __init__(self, lsw=False):
        """
        creates the Elo object

        lsw: bool: "low score wins"
            traditionally this is false, but if you have a game that the lower
            score is better, set this to True
        """
        self.ratingDict = {}
        self.games_completed = []
        self.low_score_wins = lsw
        self._key = dt.date.today().isoformat()

    def set_key(self, key):
        self._key = key

    def run(self, df, score_column):
        """
        takes in a pd.df and we need 3 required columns
            1)date: can be upper or lower case (we will change to lower) any date format works
            2)player: name of player, needs to be the same each time, as well as unique
            3)score_column: can be named anything, but need to pass that name to the function

        Loops through the unique dates in the df
        1) checks if the date has already been included (self.games_completed)
            1a) if it hasn't been computed yet, it continues
        2) sets the current_df (temp) to a single date getting all scores for that date
        2a) removes any duplicates and keeps the last answer that was given
        3) sets the index to players names and strips removing any leading or trailing spaces
        4) calls process elo to do the computing
        5) shows the updated elos
        6) adds the date to the list of completed games
        """
        df.rename(columns={"Date": "date", "Player": "player"}, inplace=True)
        try:
            df = df[["date", score_column, "player"]]
        except KeyError:
            raise KeyError(
                "PLEASE include 'date' and {} in your df as headers".format(
                    score_column
                )
            )

        for game_date in df["date"].unique():
            # 1
            if game_date not in self.games_completed:
                logging.info("EVALUATING {}".format(game_date))
                self.set_key(game_date)
                # 2
                current_df = df.loc[df["date"] == game_date].copy()
                # 2a
                current_df = current_df.loc[
                    ~current_df[["date", "player"]].duplicated(keep="last")
                ].copy()
                # 3
                current_df.index = current_df["player"].str.strip()
                # 4
                self.process_elo(pd.DataFrame(current_df[score_column]))
                # 5
                self.show_elo()
                # 6
                self.games_completed.append(game_date)

    def addPlayer(self, name, rating=1500):
        """
        creates a player and sets their rating to the default 1500
        (starting ELO can be changed with passing in a param of rating)
        """
        self.ratingDict[name] = {"ELO": rating, "historical": []}
        self.update_historical(name)

    def update_historical(self, name):
        """
        updates the historical section of the ratingDict.
        takes in a name (of a player) and creates a new dictionary in the
        historical list
        """
        self.ratingDict[name]["historical"].append(
            {self._key: self.ratingDict[name]["ELO"]}
        )

    def show_elo(self, drop=True, game_count=True, show_last_played=False):
        """
        returns the current elos as a pd.df

        defaults to removing inactive players, change by drop = False
        defaults to adding a columns for Games Playeed, change by game_count = False
        """
        self.df = self.get_df(drop_inactive=drop)

        self.active_elo = pd.DataFrame(
            self.df.tail(1).T.values, columns=["ELO"], index=self.df.T.index
        )
        self.active_elo = self.active_elo.sort_values(
            by="ELO", ascending=False
        ).reset_index()
        self.active_elo.index.name = "Rank"
        self.active_elo.columns = ["Player", "ELO"]
        self.active_elo.index += 1
        self.active_elo = self.active_elo.reset_index()

        if game_count:
            self.active_elo["Games Played"] = [
                len(self.ratingDict[x]["historical"]) - 1
                for x in self.active_elo["Player"]
            ]
        if show_last_played:
            self.active_elo = self.active_elo.set_index("Player").merge(
                self.get_last_time_played(True), left_index=True, right_index=True
            )
        return self.active_elo.round(0)

    def get_elo(self, player_name):
        """
        returns the ELO value (int) of a specific player
        """
        return self.ratingDict[player_name]["ELO"]

    def update_elo_mass(self, player_elo_dict):
        """
        takes in a dictionary
        dict.keys = players
        dict.values = players' ELO
        example: {'John':1500,'Sammy':1600}
        """
        for player in player_elo_dict:
            self.ratingDict[player]["ELO"] = player_elo_dict[player]
            self.update_historical(player)

    def get_new_elo(self, df):
        """
        takes a df that has been cleaned and columns added with the "process_elo"
        function.

        This function calculates the new elo for each of the players in the df

        returns that df

        """
        for index, row in df.iterrows():
            df.loc[index, "new_elo"] = self.one_vs_many(
                row["starting_elo"], list(row["elo_comp"]), row["wins"]
            )

        self.update_elo_mass(df["new_elo"].to_dict())

    def process_elo(self, df):
        """
        takes in a df of score objects
        df.index = player names
        df.column (one column only) player scores

        1) gets number of wins (1=win, 0=loss, .5=draw)
        2) initialize starting_elo and elo_comp (list of all compteitors elos) columns

        Loop through players

        3a) gets the starting elo (snapshot of current elo)
        3b) if the player does not exist, we create them, and set their elo to 1500
        4)  gets elo_comp data (all of your competitors elos) also a snapshot
        5) sends our df with new columns to calculate the new elo
        """
        # 1
        df["wins"] = self.num_wins(df)
        # 2
        df["starting_elo"] = None
        df["elo_comp"] = None
        opp_elos = {}
        for x in df.index:
            try:
                # 3a
                df.loc[x, "starting_elo"] = self.get_elo(x)
            except KeyError:
                try:
                    # 3b
                    self.addPlayer(x)
                    df.loc[x, "starting_elo"] = self.get_elo(x)
                except:
                    logging.error("Could not grab ELO. In Process Elo Function")
        # 4
        for x in df.index:
            opp_elos[x] = list(df.loc[df.index != x]["starting_elo"].values)

        df["elo_comp"] = opp_elos.values()

        # 5
        self.get_new_elo(df)

    def one_vs_one(self, winner, loser):
        """
        Gets the expected result (result)

        and then updates thes elos based on who won, and who lost

        use this for one vs one specifically (not groups)
        """
        result = self.expected_outcome(
            self.ratingDict[winner]["ELO"], self.ratingDict[loser]["ELO"]
        )

        self.ratingDict[winner]["ELO"] = self.ratingDict[winner]["ELO"] + (self.k) * (
            1 - result
        )
        self.ratingDict[loser]["ELO"] = self.ratingDict[loser]["ELO"] + (self.k) * (
            0 - (1 - result)
        )

    def one_vs_many(self, player_elo, opp_elo_ranks, actual_result):
        """
        takes in a players name, and then calculates their new elo based on a group of scores
        opp_elo_ranks needs to be a list of ints (elo rankings)
        actual_result: list of wins/loses (1/0's)
        """
        k = self.get_k_value(player_elo)

        expected_result = []
        for x in opp_elo_ranks:
            expected_result.append(self.expected_outcome(player_elo, x))

        if isinstance(actual_result, list):
            updated_elo = player_elo + (k * (sum(actual_result) - sum(expected_result)))
        if isinstance(actual_result, int) or isinstance(actual_result, float):
            updated_elo = player_elo + (k * ((actual_result) - sum(expected_result)))

        return updated_elo

    def expected_outcome(self, p1, p2):
        """
        takes in 2 players ELO
        returns the propability of p1 (first player entered) winning
        """
        exp = (p2 - p1) / 400.0

        return 1 / ((10.0 ** (exp)) + 1)

    def num_wins(self, col):
        """
        designed for score based events with multiple entrants
        every player that you score higher than, counts as a win (1 point)
        players that score higher than you count as a loss (0 points)
        players that tie your score you will get half (.5 points)

        this function will return the number of wins you had
        """
        return len(col) - col.rank(ascending=self.low_score_wins)

    def get_k_value(self, x):
        """
        x is the current elo of a player, this will help determine what their k factor is

        SCALE:
        1851 +   : 8
        1750-1850: 10
        1650-1750: 15
        1550-1650: 18
        1450-1550: 20
        1350-1450: 22
        1250:1350: 25
        1150-1250: 30
        1150 -   : 32

        """
        cond = [
            x > 1850,
            1750 <= x <= 1850,
            1650 <= x < 1750,
            1550 <= x < 1650,
            1450 <= x < 1550,
            1350 <= x < 1450,
            1250 <= x < 1350,
            1150 <= x < 1250,
            x < 1150,
        ]
        res = [8, 10, 15, 18, 20, 22, 25, 30, 32]
        return np.select(cond, res)

    def plot_elo_history(self, leg=True):
        """
        PLOTS (matplotlib) the ELO df using plot_date

        returns the df used (self.get_df) as well
        """
        df = self.get_df(drop_inactive=True)
        f, ax = plt.subplots(1, 1)
        plt.xlabel("date")
        plt.ylabel("elo")
        for x in df.columns:
            ax.plot_date(df.index, df[x], linestyle="-")
        if leg:
            ax.legend(labels=df.columns, loc="upper left")
        plt.gcf().autofmt_xdate()
        plt.show()

        return df

    def get_df(self, drop_inactive=False):
        """
        Creates as pd.df of all historical ELOs (does not include
        starting ELO - 1500 -  in the DF).

        this function fills NAN values with the most recent (ffill no limit)

        returns a df with date as index and each player who has participated
        in the league as columns. Values are ELOs through time.

        optional: include the "start elo" = 1500 for all players (not recomended)
        """
        players = pd.DataFrame(index=pd.to_datetime(self.games_completed))
        players.index.name = "date"
        # players.index = pd.to_datetime(players.index).strftime("%m/%d/%Y")

        for p in self.ratingDict:
            items = [(l.keys(), l.values()) for l in self.ratingDict[p]["historical"]]
            df = pd.DataFrame(items)
            df[0] = df[0].apply(pd.Series)
            df[1] = df[1].apply(pd.Series)
            df = df.rename(columns={0: "date", 1: p})
            df = df.set_index("date")
            df.index = pd.to_datetime(df.index)
            # df.index = pd.to_datetime(df.index).strftime("%m/%d/%Y")
            players = pd.concat([players, df.iloc[1:]], axis=1)
            # format the created df
            players = players.sort_index()
            players = players.dropna(axis=0, how="all")
            players = players.fillna(method="ffill")

        if drop_inactive:
            self.inactive_players = (
                (players.tail(4).diff().sum() == 0)
                .loc[(players.tail(4).diff().sum() == 0)]
                .index
            )
            new_players = (
                (players.tail(4).count() == 1).loc[players.tail(4).count() == 1].index
            )
            self.inactive_players = list(self.inactive_players)
            for player in new_players:
                self.inactive_players.remove(player)
            players = players.drop(columns=self.inactive_players)

        return players.round(0)

    def show_all_players(self) -> pd.DataFrame:
        """
        method for outputing all players for a given league as a df
        the df has 5 columns (plus an index that would be rank-1)
        Rank, Name, Current ELO, Last Played Date, Days Since Last Play
        """
        df = self.show_elo(drop=False)

        last = {}

        for name, data in self.ratingDict.items():
            last[name] = list(data["historical"][-1].keys())[0]

        # format the last played df to included last played date and days since last play
        last_played = pd.DataFrame([last]).T
        last_played.index.name = "Player"
        last_played.columns = ["Last Played Date"]
        last_played["Last Played Date"] = pd.to_datetime(
            last_played["Last Played Date"]
        )
        last_played["Days Since Last Play"] = (
            last_played["Last Played Date"] - dt.datetime.today()
        ).dt.days

        return df.merge(last_played, on="Player", how="left")

    def winners_and_losers(self):
        """
        returns a pd df listing each time the elo was reconsidered, who
        had the biggest increase and who had the biggest decrease as well
        as what % increase/decrease that was
        """
        df = self.get_df()
        change_df = pd.DataFrame(index=df.index)

        # highest person & Increase & percent
        change_df = change_df.merge(
            pd.DataFrame(df.pct_change().idxmax(axis=1)), on="date"
        )
        change_df = change_df.merge(
            pd.DataFrame(df.diff(axis=0).max(axis=1)).round(0), on="date"
        )
        change_df = change_df.merge(
            pd.DataFrame(df.pct_change().max(axis=1) * 100), on="date"
        )

        # highest person & decrease & percent
        change_df = change_df.merge(
            pd.DataFrame(df.pct_change().idxmin(axis=1)), on="date"
        )
        change_df = change_df.merge(
            pd.DataFrame(df.diff(axis=0).min(axis=1)).round(0), on="date"
        )
        change_df = change_df.merge(
            pd.DataFrame(df.pct_change().min(axis=1) * 100), on="date"
        )

        change_df.columns = [
            "biggest winner",
            "elo increase",
            "pct increase",
            "biggest loser",
            "elo decrease",
            "pct decrease",
        ]

        return change_df.dropna()

    def remove_contest(self, key):
        if key in self.games_completed:

            for name in self.ratingDict:
                for contest in self.ratingDict[name]["historical"]:
                    if list(contest.keys())[0] == key:
                        self.ratingDict[name]["historical"].remove(contest)

            self.games_completed.remove(key)

    def set_elo_to_last_score(self):
        """assigns everyone's elo to the last score"""
        for name in self.ratingDict:
            try:
                self.ratingDict[name]["ELO"] = list(
                    self.ratingDict[name]["historical"][-1].values()
                )[0]
            except IndexError:
                # if we get an index error, that means we don't have any elements
                # reset to starting value
                self.ratingDict[name]["ELO"] = 1500

    def highest_elo(self):
        """returns highest all time elo"""
        return {self.get_df().max().idxmax(): self.get_df().max().max()}

    def lowest_elo(self):
        """returns lowest all time elo"""
        return {self.get_df().min().idxmin(): self.get_df().min().min()}

    def get_last_time_played(self, as_df: bool = False):
        last_played = {
            k: list(v["historical"][-1].keys())[0] for k, v in self.ratingDict.items()
        }
        if as_df:
            return pd.DataFrame([last_played]).T
        return last_played

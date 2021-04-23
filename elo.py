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

class Elo:
    
    def __init__(self,lsw = True):
        self.ratingDict  	= {}	
        self.games_completed = []
        self.low_score_wins = lsw
        
        '''
        TODO
        self.player_list = []
        self.historical_df = None
        '''
        
    def run(self,df,score_column):
        '''
        takes in a pd.df and we need 3 required columns
            1)date: can be upper or lower case (we will change to lower) any date format works
            2)player: name of player, needs to be the same each time, as well as unique
            3)score_column: can be named anything, but need to pass that name to the function
        
        Loops through the unique dates in the df
        1) checks if the date has already been included (self.games_completed) 
            1a) if it hasn't been computed yet, it continues
        2) sets the current_df (temp) to a single date getting all scores for that date
        3) sets the index to players names and strips removing any leading or trailing spaces
        4) calls process elo to do the computing
        5) shows the updated elos
        6) adds the date to the list of completed games
        '''
        df.rename(columns={'Date':'date','Player':'player'},inplace=True)
        try:
            df = df[['date',score_column,'player']]
        except KeyError:
            print("PLEASE include 'date' and {} in your df as headers".format(score_column))
            

        for game_date in df['date'].unique():
            #1
            if game_date not in self.games_completed:
                print('EVALUATING {}'.format(game_date))
                #2
                current_df = df.loc[df['date'] == game_date].copy()
                #3
                current_df.index = current_df['player'].str.strip()
                #4
                self.process_elo(pd.DataFrame(current_df[score_column]))
                #5
                self.show_elo()
                #6
                self.games_completed.append(game_date)
    
    def addPlayer(self,name,rating = 1500):
        '''
        creates a player and sets their rating to the default 1500 
        (starting ELO can be changed with passing in a param of rating)
        '''
        self.ratingDict[name] = {'ELO':rating,'historical':[]}
        self.update_historical(name)
        '''
        TODO
        self.player_list.append(Player(name,rating,k))
		'''
    def update_historical(self,name):
        '''
        updates the historical section of the ratingDict.
        takes in a name (of a player) and creates a new dictionary in the 
        historical list 
        '''
        self.ratingDict[name]['historical'].append({dt.date.today().isoformat():self.ratingDict[name]['ELO']})
        
    def show_elo(self,player_name=None):
        '''
        prints to console the current elos of all players currently in the 
        ratingDict.
        
        Also returns the current elos as a dict
        
        optional: pass in player name param and get back a text of selected
        player's ELO 
        '''
        elo_df = pd.DataFrame(self.ratingDict).T.sort_values(by='ELO',ascending=False)['ELO']
        elo_df = elo_df.reset_index()
        elo_df.reset_index(inplace=True)
        elo_df.columns = ['Rank','Player','ELO']
        elo_df['Rank']+=1
        
        if player_name == None:
            print(elo_df)
        else:
            print('{}\'s Current Elo: {}'.format(player_name,self.get_elo(player_name)))
        
        return elo_df
        
    def get_elo(self,player_name):
        '''
        returns the ELO value (int) of a specific player
        '''
        return self.ratingDict[player_name]['ELO']
        
    def update_elo_mass(self,player_elo_dict):
        '''
        takes in a dictionary 
        dict.keys = players
        dict.values = players' ELO 
        example: {'John':1500,'Sammy':1600}
        '''
        for player in player_elo_dict:
            self.ratingDict[player]['ELO'] = player_elo_dict[player]
            self.update_historical(player)
            
    def get_new_elo(self, df):
        '''
        takes a df that has been cleaned and columns added with the "process_elo"
        function.
        
        This function calculates the new elo for each of the players in the df
        
        returns that df
        
        '''
        for index, row in df.iterrows():
            df.loc[index,'new_elo'] = self.one_vs_many(row['starting_elo'],list(row['elo_comp']),row['wins'])
        
        self.update_elo_mass(df['new_elo'].to_dict())
        
    
    def process_elo(self,df):
        '''
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
        '''
        #1
        df['wins'] = self.num_wins(df)
        #2 
        df['starting_elo'] = None
        df['elo_comp'] = None
        opp_elos = {}
        for x in df.index:
            try:
                #3a
                df.loc[x,'starting_elo'] = self.get_elo(x)
            except KeyError:
                try:
                    #3b
                    self.addPlayer(x)
                    df.loc[x,'starting_elo'] = self.get_elo(x)
                except:
                    print('Could not grab ELO')
        #4
        for x in df.index:
            opp_elos[x] = list(df.loc[df.index !=x]['starting_elo'].values)
            
        df['elo_comp'] = opp_elos.values()
        
        #5
        self.get_new_elo(df)
    
    def one_vs_one(self, winner, loser):
        '''
        Gets the expected result (result) 
        
        and then updates thes elos based on who won, and who lost
        
        use this for one vs one specifically (not groups)
        '''
        result = self.expected_outcome(self.ratingDict[winner]['ELO'], self.ratingDict[loser]['ELO']  )
        
        self.ratingDict[winner]['ELO'] = self.ratingDict[winner]['ELO'] + (self.k)*(1 - result)  
        self.ratingDict[loser]['ELO'] 	= self.ratingDict[loser]['ELO'] + (self.k)*(0 - (1 -result))
    		
    def one_vs_many(self,player_elo,opp_elo_ranks,actual_result):
        '''
        takes in a players name, and then calculates their new elo based on a group of scores
        opp_elo_ranks needs to be a list of ints (elo rankings)
        actual_result: list of wins/loses (1/0's) 
        '''       
        k = self.get_k_value(player_elo)
        
        expected_result = []
        for x in opp_elo_ranks:
            expected_result.append(self.expected_outcome(player_elo,x))
            
        if isinstance(actual_result,list):
            updated_elo = (player_elo + (k*(sum(actual_result)-sum(expected_result))))
        if isinstance(actual_result,int) or isinstance(actual_result,float):
            updated_elo = (player_elo + (k*((actual_result)-sum(expected_result))))
            
        return updated_elo
        
    def expected_outcome(self, p1, p2):
        '''
        takes in 2 players (need to be in the self.ratingDict)
        returns the propability of p1 (first player entered) winning
        '''
        exp = (p2-p1)/400.0
        
        return 1/((10.0**(exp))+1)
    
    def num_wins(self,col):
        '''
        designed for score based events with multiple entrants
        every player that you score higher than, counts as a win (1 point)
        players that score higher than you count as a loss (0 points)
        players that tie your score you will get half (.5 points)
        
        this function will return the number of wins you had
        '''
        return len(col) - col.rank(ascending=self.low_score_wins)

    def get_k_value(self,x):
        '''
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

        '''
        cond = [
            x>1850,
            1750<=x<=1850,
            1650<=x<1750,
            1550<=x<1650,
            1450<=x<1550,
            1350<=x<1450,
            1250<=x<1350,
            1150<=x<1250,
            x<1150
            ]
        res = [8,
               10,
               15,
               18,
               20,
               22,
               25,
               30,
               32
               ]
        return np.select(cond,res)

    def plot_elo_history(self,leg = True):
        '''
        PLOTS (matplotlib) the ELO df using plot_date
        
        returns the df as well
        '''
        df = self.get_df()
        f, ax = plt.subplots(1, 1)
        plt.xlabel('date')
        plt.ylabel('elo')
        for x in df.columns:
            ax.plot_date(df.index,df[x],linestyle="-")
        if leg:
            ax.legend(labels = df.columns,loc = 'upper left')
        plt.gcf().autofmt_xdate()
        plt.show()
        
        return df
        
    def get_df(self,add_start=False,drop_inactive=False):
        '''
        Creates as pd.df of all historical ELOs (does not include 
        starting ELO - 1500 -  in the DF). 
        
        this function fills NAN values with the most recent (ffill no limit)
        
        returns a df with date as index and each player who has participated
        in the league as columns. Values are ELOs through time.
        
        optional: include the "start elo" = 1500 for all players (not recomended)
        '''
        players = pd.DataFrame(index = pd.to_datetime(self.games_completed))
        players.index.name = 'date'
        
        for p in self.ratingDict:
            d = []
            e = []
            for elo in self.ratingDict[p]['historical']:
                d.append(list(elo.keys())[0])
                e.append(list(elo.values())[0])
            indv = pd.DataFrame(e,index=pd.to_datetime(d),columns=[p])
            indv.index.name = 'date'
            indv = indv.reset_index()
            players = players.merge(indv.drop(0,axis=0),how='outer',on='date')
            #format the created df
            players.index = players['date']
            players = players.drop('date',axis=1)
            players = players.sort_index()
            players = players.dropna(axis=0,how='all')
            players = players.fillna(method='ffill')

            
        if add_start:
            #add optional start column
            players.loc['start'] = np.ones(len(players.columns))*1500
        
        if drop_inactive: 
            self.inactive_players = (players.tail(3).diff().sum()==0).loc[(players.tail(3).diff().sum()==0)].index
            return players.drop(columns=self.inactive_players)
        else:
            return players
    
    def winners_and_losers(self):
        
        df = self.get_df()
        change_df = pd.DataFrame(index = df.index)
        
        #highest person & Increase & percent
        change_df = change_df.merge(pd.DataFrame(df.pct_change().idxmax(axis=1)),on='date')
        change_df = change_df.merge(pd.DataFrame(df.diff(axis=0).max(axis=1)),on='date')
        change_df = change_df.merge(pd.DataFrame(df.pct_change().max(axis=1)),on='date')

        #highest person & decrease & percent
        change_df = change_df.merge(pd.DataFrame(df.pct_change().idxmin(axis=1)),on='date')
        change_df = change_df.merge(pd.DataFrame(df.diff(axis=0).min(axis=1)),on='date')
        change_df = change_df.merge(pd.DataFrame(df.pct_change().min(axis=1)),on='date')

        
        change_df.columns = ['biggest winner','elo increase','pct increase', 'biggest loser','elo decrease','pct decrease']
        
        return change_df.dropna()
'''

TODO
Add a player class to make things easier?

'''   
class Player():
    def __init__(self,name,k,elo=1500):
        self.k = k
        self.elo = elo
        self.historical_elo = []
        











    
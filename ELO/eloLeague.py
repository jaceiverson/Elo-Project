"""
I have created 2 custom modules that pickle objects
You can create your own, or find mine here:
    https://github.com/jaceiverson/custom-python/blob/master/general.py
"""
import sys
sys.path.append('/Users/techseoremote2/Documents')
from custom_python.general import pickle_read,pickle_write
from elo import Elo

def generic_league(df,
                   score_column,
                   file_path = './pickled-elo.p',
                   lsw=False,
                   save=True):
    '''
    df: pd.df: where the scores are recored. This has 3 required columns.
        Two of those columns must be named 'Date' and 'Player' 
        (captialization does not matter)
        The other needs to contain the score.
   
    score_column: string: name of column in df that holds the score
    
    file_path: string: path whre you would like to save your league
    
    lsw: bool: Low Score Wins. If you play a game where low score wins, pass in True
    
    save: bool: if you would like to save your league to the designated spot.
                if you want a temporary score, 
                or see temporary results, I recomend leaving this False
    
    ::Steps::
        1) Create the elo League object
        2) it will attempt to read from your pickled file
            it updates the rating dictionary as well as the completed games
        3) It calls the .run() function that will calculate elo
            this will calculate for every date found that is not included
            in the ".games_completed" variable (list) of the league object
        4) Once complete, it will save back to the designated file location
        5) Returns the leauge object
    '''
    #1
    league = Elo(lsw=lsw)
    #2
    try:
        league.ratingDict = pickle_read(file_path).ratingDict
        league.games_completed = pickle_read(file_path).games_completed
        print('LEAGUE FROM PICKLE')
    except:
        print('NEW LEAGUE')

    #3 run the algo
    league.run(df,score_column)

    #4 save for later
    if save:
        print("SAVING")
        pickle_write(file_path,league)
    #5
    return league
# Elo-Project
Custom Elo Class that was inspired by another github user:<br>
    https://github.com/ddm7018/Elo/blob/master/elosports/elo.py
    
ELO FORMULAS used were found on wiki:<br>
    https://en.wikipedia.org/wiki/Elo_rating_system

Based on traditional a Elo formula, I have developed a class that incorporates the *pandas library* to create custom Elo ratings for any contest. Elo takes in a pandas DataFrame of scores, compares the scores of multiple people, then calculates the elo. It then stores the Elo object in pickle (<a href=https://github.com/jaceiverson/custom-python/blob/master/general.py>I have a</a> simple pickle_read & pickle_write functions, that you can use, or just write one yourself). 

To start using call the generic_league function found in eloLeauge.py
```
generic_league(df,
                score_column,
                file_path = './pickled-elo.p,
                lsw = False,
                save = True
                )
```
__Parameters__
 - Pandas DataFrame
     - In your df you must have 2 columns (case insensitive):
        - Date
        - Player
        - A Score Column (any name)
- Name of the score column (str)

__Optional Parameters__
- File path 
    - Defaults to ./pickled-elo.p
- lsw (Low Score Wins)
    - Defaults to False
    - Set to True if you are playing a game where the lower score would win
- save 
    - Defaults to True
    - This is if you would like to save your Elo Object to pickle
    - Can be set to False if you would like to see a temporary result, or for testing


__Notes__
- Elo starts at 1500 and will fluctuate on results
- Expect to see drastic changes at the start, but as you get more results the elo will become consistent
- Default file path (if not passed in) will be in the cwd and titled pickled-elo.p
- Class will add new players as their names show up on the list
- Drop_inactive removes from output (but still saves) players that haven't participated in the last 3 events

I have integrated mine with Google Sheets using the <a href=https://pygsheets.readthedocs.io/en/stable/>Pygsheets</a> method: 
```
.set_dataframe()
```
 - To save/see the current elos 
```
self.show_elo()
```
 - To save/see the historical elos
```
self.get_df()
```
 - To save/see the winners and losers
```
self.winners_and_losers()
```

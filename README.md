# Elo-Project
Custom Elo Class that was inspired by another github user:<br>
    https://github.com/ddm7018/Elo/blob/master/elosports/elo.py
    
ELO FORMULAS used were found on wiki:<br>
    https://en.wikipedia.org/wiki/Elo_rating_system

Based on an Elo formula from wikipedia, I have developed a class that incorporates the *pandas library* to create custom Elo ratings for any contest. Elo takes in a pandas DataFrame of scores, compares the scores of multiple people, then calculates the elo. It then stores the Elo object in pickle (<a href=https://github.com/jaceiverson/custom-python/blob/master/general.py>I have a</a> simple pickle_read & pickle_write functions, that you can use, or just write one yourself). 

To start using call the generic_league function found in eloLeauge.py. This can work for multiple events at once, or a singular event. At the moment, it evaluates on date, so only one event per date for now, but I hope to change that to have a unique key for each activity so you can incorporate multiple events in the same day.

```
generic_league(df,
                score_column,
                file_path = './pickled-elo.p,
                lsw = False,
                save = True
                )
```
__Parameters__
 - df
     - type: pandas DataFrame
     - In your df you must have 2 columns (case insensitive):
        - Date
        - Player
        - A Score Column (any name)
- score_column
    - type: string
    - Name of the score column (str)

__Optional Parameters__
- file_path
    - type: string
    - Defaults to ./pickled-elo.p
- lsw (Low Score Wins)
    - type: bool
    - Defaults to False
    - Set to True if you are playing a game where the lower score would win
- save
    - type: bool
    - Defaults to True
    - This is if you would like to save your Elo Object to pickle
    - Can be set to False if you would like to see a temporary result, or for testing

__Returns__
elo object

__Notes__
- Elo starts at 1500 and will fluctuate on results
- Expect to see drastic changes at the start, but as you get more results the elo will become consistent
- Default file path (if not passed in) will be in the cwd and titled pickled-elo.p
- Class will add new players as their names show up on the list
- Drop_inactive removes from output (but still saves) players that haven't participated in the last 3 events

I have integrated a custom league for weekly work activity with Google Sheets using the <a href=https://pygsheets.readthedocs.io/en/stable/>Pygsheets</a> method: 
```
.set_dataframe()
```
I use that to save the following to different tabs in a Google Sheet. This was the easiest way for everyone to see the scores.

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

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 17:09:13 2021

@author: jiverson
"""

from elo import Elo
import pandas as pd

import sys
sys.path.append("/Users/techseoremote2/Documents/custom_python")
from custom_modules import pickle_write, pickle_read
from gsheets_con import connect

import matplotlib.pyplot as plt

def gg_league(save=True):
    #1
    google_sheets_in = connect('TASK REVIEW').worksheet('title','Indv League')
    google_sheets_out = connect('TASK REVIEW')
    
    #2
    df = google_sheets_in.get_as_df(start='a1')
    df['Total Score'] = df['Total Score'].str.replace(',','').astype(int)
    
    file_path = './GG/gg-league-obj.p'

    #3
    gg = generic_league(df,'Total Score',file_path,save=save,lsw=False)
    
    #6
    '''
    connect('TASK REVIEW','Current ELOs')\
            .set_dataframe(league.get_df().sort_values(by='date',ascending=False),
                           start='h1',
                           copy_index = True)

    '''
    if save:
        google_sheets_out.worksheet('title','Current ELOs').set_dataframe(gg.show_elo(),start='a1',copy_index=False)
        
        google_sheets_out.worksheet('title','ELO HISTORY').set_dataframe(gg.get_df(drop_inactive=True),start='a1',copy_index=True)
        
        google_sheets_out.worksheet('title','Biggest ELO Movers').set_dataframe(gg.winners_and_losers(),start='a1',copy_index=True)
        
    return gg
    
def kwf_league(save=True):
    #1
    google_sheets_in = connect('Keyword Friday | Terakeet').worksheet('title','detailed_game_log')
    google_sheets_out = connect('Keyword Friday | Terakeet')
    
    #2
    
    df = google_sheets_in.get_as_df(start='a1')
    try:
        df['Delta'] = df['Delta'].str.replace(',','').astype(int)
    except:
        df['Delta'] = df['Delta'].astype(int)
    
    file_path = './KWF/kwf-league.p'
    
    #to step 3
    kwf = generic_league(df,'Delta',file_path,save=save,lsw=True)
    
    #6 writing to google sheets
    if save:
        google_sheets_out.worksheet('title','KWF ELO').set_dataframe(kwf.show_elo(),start='a1',copy_index=False)
        
        google_sheets_out.worksheet('title','KWF ELO HISTORY').set_dataframe(kwf.get_df(),start='a1',copy_index=True)
    
        google_sheets_out.worksheet('title','ELO Winners/Loosers').set_dataframe(kwf.winners_and_losers(),start='a1',copy_index=True)
    
    return kwf
    

def generic_league(df,score_column,file_path,lsw=False,save=True):
    #3
    league = Elo(lsw=lsw)
    #will read data from pickle if it exists
    try:
        league.ratingDict = pickle_read(file_path).ratingDict
        league.games_completed = pickle_read(file_path).games_completed
        print('LEAGUE FROM PICKLE')
    except:
        print('NEW LEAGUE')
        
    #4 run the algo
    league.run(df,score_column)
    
    #5 save for later
    if save:
        print("SAVING")
        pickle_write(file_path,league)
    
    return league
    
    
if __name__=='__main__':
    '''
    1) Get the data from google sheets
    2) Clean the data to make sure there are not issues
        a) mainly need to make sure that total score is an int
    
    --GENERIC LEAGUE FUNCTION--
    
    3) Make the ELO object
        a) will look for an existing ELO object in pickle, 
            if not found will create another one
    
    4) Loop through each game, and adjust the ELO accordingly
        a) make sure that current date, has not been evaluated yet
        b) create a df of just that dates competition
        c) change the index to be the players name
        d) get the starting elo, number of wins, and calculate new elo
            also update the elos in the ELO object
        e) print new ELOS to console
        f) once done with this date, add the date to the games_completed list
    
    --OPTIONAL STEPS--
    
    5) Write the ELO object to pickle to use later
    6) Post the current data to the google sheet
    '''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 22 16:19:24 2021

@author: techseoremote2
"""
import  sys
sys.path.append("/Users/techseoremote2/Documents/")
from custom_python.general import pickle_read,pickle_write
from elo import Elo

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
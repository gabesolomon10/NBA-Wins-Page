from __future__ import absolute_import, print_function
from flask import Flask, render_template, request, redirect, flash, url_for
from flaskext.mysql import MySQL

# caching imports
from flask_caching import Cache

# Other stuff
import requests, time, sys, re, lxml, html5lib, scipy, openpyxl, os, functools
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import ast
import wget

from functools import reduce 
from datetime import date, timedelta
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguestandings

app = Flask(__name__)
cache = Cache(app,config={'CACHE_TYPE': 'simple'})
app.secret_key = 'a;sldks;js?##s;kasjjdfjd'

mysql = MySQL()
mysql.init_app(app)

@app.route("/")
#Get the standings
def home():

	standings = leaguestandings.LeagueStandings()
	standings_df = standings.get_data_frames()[0]


	# Set up the teams
	teams = pd.DataFrame({'Team Name': ['Team Nebeyu', 'They all start with 0 wins', 
	                                    "Our friend is an alcoholic and it's troubling", "Sammy Ps AF1s Est. 2011",
	                                    "Pre-pubescent toddler",
	                                    "Did it",
	                                    "Benjamin Bogdanovic"],
	                      'Owner': ['Nebeyu', 'Phil', 'Fitz', 'Cepehr', 'Gabe', 'Young', 'Ben'],
	                      'Team 1': ['Bucks','76ers', 'Clippers','Rockets','Nuggets', 'Lakers', 'Celtics'],
	                      'Team 2': ['Spurs', 'Blazers', 'Nets', 'Pacers', 'Raptors', 'Warriors', 'Jazz'],
	                      'Team 3': ['Heat', 'Mavericks', 'Magic', 'Pelicans', 'Timberwolves','Pistons', 'Hawks'],
	                      'Team 4': ['Grizzlies', 'Knicks', 'Wizards', 'Suns', 'Thunder', 'Bulls', 'Kings']})


	#Create the wins table
	merged_wins = teams.merge(standings_df, left_on = 'Team 1', right_on = 'TeamName')
	merged_wins = merged_wins[['Team Name','Owner', 'Team 1', 'PreAS', 'Team 2', 'Team 3', 'Team 4']]
	merged_wins = merged_wins.rename(columns= {"PreAS": 'Team 1 Wins'})

	merged_wins = merged_wins.merge(standings_df, left_on = 'Team 2', right_on = 'TeamName')
	merged_wins = merged_wins[['Team Name','Owner', 'Team 1', 'Team 1 Wins', 'Team 2', 'PreAS', 'Team 3', 'Team 4']]
	merged_wins = merged_wins.rename(columns= {"PreAS": "Team 2 Wins"})

	merged_wins = merged_wins.merge(standings_df, left_on = 'Team 3', right_on = 'TeamName')
	merged_wins = merged_wins[['Team Name','Owner', 'Team 1', 'Team 1 Wins', 'Team 2', 'Team 2 Wins',
	                           'Team 3', 'PreAS', 'Team 4']]
	merged_wins = merged_wins.rename(columns= {"PreAS": "Team 3 Wins"})

	merged_wins = merged_wins.merge(standings_df, left_on = 'Team 4', right_on = 'TeamName')
	merged_wins = merged_wins[['Team Name','Owner', 'Team 1', 'Team 1 Wins',
	                           'Team 2', 'Team 2 Wins',
	                           'Team 3', 'Team 3 Wins', 'Team 4', 'PreAS']]
	merged_wins = merged_wins.rename(columns= {"PreAS": "Team 4 Wins"})

	return render_template('simple.html',  tables=[merged_wins.to_html(classes='data')], titles=merged_wins.columns.values)


if __name__ == "__main__":
    app.run(debug=True)






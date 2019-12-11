from __future__ import absolute_import, print_function
from flask import Flask, render_template, request, redirect, flash, url_for
from flaskext.mysql import MySQL
import requests
from lxml.html import fromstring
from itertools import cycle
import traceback

# caching imports
from flask_caching import Cache

# Other stuff
import requests, time, re, html5lib, scipy, openpyxl, os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import wget

from datetime import date, timedelta
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguestandings

logos_folder = os.path.join('static', 'nba_logos')
pics_folder = os.path.join('static', 'profiles')

app = Flask(__name__)
app.config['nba_folder'] = logos_folder
app.config['profiles_folder'] = pics_folder

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
	                      'Owner': [os.path.join(app.config['profiles_folder'],'nebeyu.png'),
									os.path.join(app.config['profiles_folder'],'phil.png'),
									os.path.join(app.config['profiles_folder'],'fitz.png'),
									os.path.join(app.config['profiles_folder'],'cepehr.png'),
									os.path.join(app.config['profiles_folder'],'gabe.png'),
									os.path.join(app.config['profiles_folder'],'young.png'),
									os.path.join(app.config['profiles_folder'],'ben.png')],
	                      'Team 1': ['Bucks','76ers', 'Clippers','Rockets','Nuggets', 'Lakers', 'Celtics'],
	                      'Team 2': ['Spurs', 'Trail Blazers', 'Nets', 'Pacers', 'Raptors', 'Warriors', 'Jazz'],
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

	merged_wins['Total Wins'] = merged_wins['Team 1 Wins'].str.extract('(.*)[-]').astype(int) \
	+ merged_wins['Team 2 Wins'].str.extract('(.*)[-]').astype(int) \
	+ merged_wins['Team 3 Wins'].str.extract('(.*)[-]').astype(int) \
	+ merged_wins['Team 4 Wins'].str.extract('(.*)[-]').astype(int)

	merged_wins['Total Losses'] = merged_wins['Team 1 Wins'].str.extract('[-](.*)').astype(int) \
	+ merged_wins['Team 2 Wins'].str.extract('[-](.*)').astype(int) \
	+ merged_wins['Team 3 Wins'].str.extract('[-](.*)').astype(int) \
	+ merged_wins['Team 4 Wins'].str.extract('[-](.*)').astype(int)

	merged_wins['Win Percentage'] = round(merged_wins['Total Wins']/(merged_wins['Total Wins']+merged_wins['Total Losses']),3)

	cols = merged_wins.columns.tolist()
	cols.insert(2, cols.pop(cols.index('Total Wins')))
	cols.insert(3, cols.pop(cols.index('Win Percentage')))
	merged_wins = merged_wins.reindex(columns= cols)

	#NBA Logos

	merged_wins['Team 1 Image'] = [os.path.join(app.config['nba_folder'],'bucks.png'),
								   os.path.join(app.config['nba_folder'],'76ers.png'),
								   os.path.join(app.config['nba_folder'],'clippers.png'),
								   os.path.join(app.config['nba_folder'],'rockets.png'),
								   os.path.join(app.config['nba_folder'],'nuggets.png'),
								   os.path.join(app.config['nba_folder'],'lakers.png'),
								   os.path.join(app.config['nba_folder'],'celtics.png')]

	merged_wins['Team 2 Image'] = [os.path.join(app.config['nba_folder'],'spurs.png'),
								   os.path.join(app.config['nba_folder'],'trail_blazers.png'),
								   os.path.join(app.config['nba_folder'],'nets.png'),
								   os.path.join(app.config['nba_folder'],'pacers.png'),
								   os.path.join(app.config['nba_folder'],'raptors.png'),
								   os.path.join(app.config['nba_folder'],'warriors.png'),
								   os.path.join(app.config['nba_folder'],'jazz.png')]

	merged_wins['Team 3 Image'] = [os.path.join(app.config['nba_folder'],'heat.png'),
								   os.path.join(app.config['nba_folder'],'mavericks.png'),
								   os.path.join(app.config['nba_folder'],'magic.png'),
								   os.path.join(app.config['nba_folder'],'pelicans.png'),
								   os.path.join(app.config['nba_folder'],'timberwolves.png'),
								   os.path.join(app.config['nba_folder'],'pistons.png'),
								   os.path.join(app.config['nba_folder'],'hawks.png')]

	merged_wins['Team 4 Image'] = [os.path.join(app.config['nba_folder'],'grizzlies.png'),
								   os.path.join(app.config['nba_folder'],'knicks.png'),
								   os.path.join(app.config['nba_folder'],'wizards.png'),
								   os.path.join(app.config['nba_folder'],'suns.png'),
								   os.path.join(app.config['nba_folder'],'thunder.png'),
								   os.path.join(app.config['nba_folder'],'bulls.png'),
								   os.path.join(app.config['nba_folder'],'kings.png')]

	merged_wins = merged_wins.sort_values(by=['Total Wins'], ascending = False)
	merged_wins.reset_index(drop=True, inplace=True)

	return render_template('responsive_table.html',  team1_data = merged_wins.iloc[0].values,
	 									   team2_data = merged_wins.iloc[1].values,
	                                       team3_data = merged_wins.iloc[2].values, 
	                                       team4_data = merged_wins.iloc[3].values,
	                                       team5_data = merged_wins.iloc[4].values, 
	                                       team6_data = merged_wins.iloc[5].values,
	                                       team7_data = merged_wins.iloc[6].values,)

if __name__ == "__main__":
    app.run(debug=True)






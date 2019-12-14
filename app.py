from flask import Flask, render_template, request, redirect, flash, url_for
from flaskext.mysql import MySQL
import requests
from bs4 import BeautifulSoup

# caching imports
from flask_caching import Cache

# Other stuff
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import wget
import os


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

	#Scrape standings from basketball-reference
	stats_page = requests.get('https://www.basketball-reference.com/leagues/NBA_2020.html')
	content = stats_page.content
	soup = BeautifulSoup(content, 'html.parser')

	western_conf = soup.find(name='table', attrs={'id': 'confs_standings_W'})
	eastern_conf = soup.find(name='table', attrs={'id': 'confs_standings_E'})

	western_str = str(western_conf)
	eastern_str = str(eastern_conf)

	western_conf_df = pd.read_html(western_str)[0]
	eastern_conf_df = pd.read_html(eastern_str)[0]

	western_conf_df = western_conf_df.rename(columns={"Western Conference": "Team"})
	eastern_conf_df = eastern_conf_df.rename(columns={"Eastern Conference": "Team"})

	#Add necessary columns to standings
	standings_df = western_conf_df.append(eastern_conf_df)

	standings_df['Team'] = standings_df['Team'].str.extract('(.*)[(]')
	standings_df['Team'] = standings_df['Team'].astype(str)
	standings_df['Team'] = standings_df['Team'].str.strip()

	standings_df["Record"] = standings_df['W'].map(str) + "-" + standings_df['L'].map(str)

	# Set up the teams
	teams = pd.DataFrame({'Team Name': ['Team Nebeyu', 
										'They all start with 0 wins', 
	                                    "Our friend is an alcoholic and it's troubling", 
	                                    "Sammy Ps AF1s Est. 2011",
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
	                      'Team 1': ['Milwaukee Bucks','Philadelphia 76ers', 'Los Angeles Clippers',
	                      			  'Houston Rockets','Denver Nuggets', 'Los Angeles Lakers', ' Boston Celtics'],
	                      'Team 2': ['San Antonio Spurs', 'Portland Trail Blazers', 'Brooklyn Nets',
                                     'Indiana Pacers', 'Toronto Raptors', 'Golden State Warriors', 'Utah Jazz'],
	                      'Team 3': ['Miami Heat', 'Dallas Mavericks', 'Orlando Magic',
                                     'New Orleans Pelicans', 'Minnesota Timberwolves','Detroit Pistons', 'Atlanta Hawks'],
	                      'Team 4': ['Memphis Grizzlies', 'New York Knicks', 'Washington Wizards', 'Phoenix Suns',
                                     'Oklahoma City Thunder', 'Chicago Bulls', 'Sacramento Kings']})

	#Create the wins table
	merged_wins = teams.merge(standings_df, left_on='Team 1', right_on='Team')

	merged_wins = merged_wins[['Team Name', 'Owner', 'Team 1', 'W', 'L', 'Record', 'Team 2', 'Team 3', 'Team 4']]
	merged_wins = merged_wins.rename(columns={"W": 'Team 1 Wins', 'L': 'Team 1 Losses', "Record": "Team 1 Record"})

	merged_wins = merged_wins.merge(standings_df, left_on='Team 2', right_on='Team')
	merged_wins = merged_wins[['Team Name', 'Owner', 'Team 1', 'Team 1 Wins', 'Team 1 Losses', 'Team 1 Record',
							   'Team 2', 'W', 'L', 'Record', 'Team 3', 'Team 4']]
	merged_wins = merged_wins.rename(columns={"W": 'Team 2 Wins', 'L': 'Team 2 Losses', "Record": "Team 2 Record"})

	merged_wins = merged_wins.merge(standings_df, left_on='Team 3', right_on='Team')
	merged_wins = merged_wins[['Team Name', 'Owner','Team 1', 'Team 1 Wins', 'Team 1 Losses', 'Team 1 Record',
							   'Team 2', 'Team 2 Wins', 'Team 2 Losses', 'Team 2 Record',
							   'Team 3', 'W', 'L', 'Record', 'Team 4']]
	merged_wins = merged_wins.rename(columns={"W": 'Team 3 Wins', 'L': 'Team 3 Losses', "Record": "Team 3 Record"})

	merged_wins = merged_wins.merge(standings_df, left_on='Team 4', right_on='Team')
	merged_wins = merged_wins[['Team Name','Owner', 'Team 1', 'Team 1 Wins', 'Team 1 Losses', 'Team 1 Record',
							   'Team 2', 'Team 2 Wins', 'Team 2 Losses', 'Team 2 Record',
							   'Team 3', 'Team 3 Wins', 'Team 3 Losses', 'Team 3 Record',
							   'Team 4', 'W', 'L', 'Record']]
	merged_wins = merged_wins.rename(columns={"W": 'Team 4 Wins', 'L': 'Team 4 Losses', "Record": "Team 4 Record"})

	merged_wins = merged_wins[['Team Name','Owner', 
	'Team 1', 'Team 1 Wins', 'Team 1 Losses', 'Team 1 Record',
							   'Team 2', 'Team 2 Wins', 'Team 2 Losses', 'Team 2 Record',
							   'Team 3', 'Team 3 Wins', 'Team 3 Losses', 'Team 3 Record',
							   'Team 4', 'Team 4 Wins', 'Team 4 Losses', 'Team 4 Record']]

	merged_wins['Total Wins'] = merged_wins['Team 1 Wins'] + merged_wins['Team 2 Wins'] +\
								merged_wins['Team 3 Wins'] + merged_wins['Team 4 Wins']

	merged_wins['Win Percentage'] = round((merged_wins['Total Wins'])/
										  (merged_wins['Total Wins'] +
										   merged_wins['Team 1 Losses'] + merged_wins['Team 2 Losses'] +
										   merged_wins['Team 3 Losses'] + merged_wins['Team 4 Losses']), 3)

	merged_wins = merged_wins[['Team Name','Owner', 'Total Wins', 'Win Percentage',
							   'Team 1', 'Team 1 Record',
							   'Team 2', 'Team 2 Record',
							   'Team 3', 'Team 3 Record',
							   'Team 4',  'Team 4 Record']]
	#NBA Logos
	merged_wins['Team 1 Image'] = pd.Series([os.path.join(app.config['nba_folder'],'bucks.png'),
								   os.path.join(app.config['nba_folder'],'76ers.png'),
								   os.path.join(app.config['nba_folder'],'clippers.png'),
								   os.path.join(app.config['nba_folder'],'rockets.png'),
								   os.path.join(app.config['nba_folder'],'nuggets.png'),
								   os.path.join(app.config['nba_folder'],'lakers.png'),
								   os.path.join(app.config['nba_folder'],'celtics.png')])

	merged_wins['Team 2 Image'] = pd.Series([os.path.join(app.config['nba_folder'],'spurs.png'),
								   os.path.join(app.config['nba_folder'],'trail_blazers.png'),
								   os.path.join(app.config['nba_folder'],'nets.png'),
								   os.path.join(app.config['nba_folder'],'pacers.png'),
								   os.path.join(app.config['nba_folder'],'raptors.png'),
								   os.path.join(app.config['nba_folder'],'warriors.png'),
								   os.path.join(app.config['nba_folder'],'jazz.png')])

	merged_wins['Team 3 Image'] = pd.Series([os.path.join(app.config['nba_folder'],'heat.png'),
								   os.path.join(app.config['nba_folder'],'mavericks.png'),
								   os.path.join(app.config['nba_folder'],'magic.png'),
								   os.path.join(app.config['nba_folder'],'pelicans.png'),
								   os.path.join(app.config['nba_folder'],'timberwolves.png'),
								   os.path.join(app.config['nba_folder'],'pistons.png'),
								   os.path.join(app.config['nba_folder'],'hawks.png')])

	merged_wins['Team 4 Image'] = pd.Series([os.path.join(app.config['nba_folder'],'grizzlies.png'),
								   os.path.join(app.config['nba_folder'],'knicks.png'),
								   os.path.join(app.config['nba_folder'],'wizards.png'),
								   os.path.join(app.config['nba_folder'],'suns.png'),
								   os.path.join(app.config['nba_folder'],'thunder.png'),
								   os.path.join(app.config['nba_folder'],'bulls.png'),
								   os.path.join(app.config['nba_folder'],'kings.png')])

	merged_wins = merged_wins.sort_values(by=['Total Wins'], ascending = False)
	merged_wins.reset_index(drop=True, inplace=True)

	return render_template('responsive_table.html',  team1_data = merged_wins.iloc[0].values,
	 									   team2_data = merged_wins.iloc[1].values,
	                                       team3_data = merged_wins.iloc[2].values, 
	                                       team4_data = merged_wins.iloc[3].values,
	                                       team5_data = merged_wins.iloc[4].values, 
	                                       team6_data = merged_wins.iloc[5].values)
	                                       #team7_data = merged_wins.iloc[6].values,)

if __name__ == "__main__":
    app.run(debug=True)






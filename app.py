#Import
from flask import Flask, render_template, request, redirect, flash, url_for
from flaskext.mysql import MySQL
import requests
from bs4 import BeautifulSoup

#Caching imports
from flask_caching import Cache

#Import other stuff
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import wget
import os
import lxml

#Set folder paths
logos_folder = os.path.join('static', 'nba_logos')
pics_folder = os.path.join('static', 'profiles')

#App setup
app = Flask(__name__)
app.config['nba_folder'] = logos_folder
app.config['profiles_folder'] = pics_folder

cache = Cache(app,config={'CACHE_TYPE': 'simple'})
app.secret_key = 'a;sldks;js?##s;kasjjdfjd'

mysql = MySQL()
mysql.init_app(app)

#Define homepage
@app.route("/", methods=['GET'])
#Get the standings
def home():

	#Scrape standings from basketball-reference
	stats_page = requests.get('https://www.basketball-reference.com/leagues/NBA_2021.html')
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

	#standings_df['Team'] = standings_df['Team'].str.extract('(.*)[(]')
	standings_df['Team'] = standings_df['Team'].astype(str)
	standings_df['Team'] = standings_df['Team'].str.replace("\([0-9]+\)", "")
	standings_df['Team'] = standings_df['Team'].str.strip()

	standings_df['W'] = standings_df['W'].replace(np.nan, 0)
	standings_df['L'] = standings_df['L'].replace(np.nan, 0)
	standings_df['W'] = standings_df["W"].round().astype(int)
	standings_df['L'] = standings_df["L"].round().astype(int)
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
	                      'Team 1': ['Milwaukee Bucks','Miami Heat', 'Brooklyn Nets',
	                      			  'Boston Celtics','Los Angeles Lakers', 'Los Angeles Clippers', 'Denver Nuggets'],
	                      'Team 2': ['Indiana Pacers', 'Philadelphia 76ers', 'Portland Trail Blazers',
                                     'Toronto Raptors', 'Phoenix Suns', 'Utah Jazz', 'Dallas Mavericks'],
	                      'Team 3': ['Golden State Warriors', 'Memphis Grizzlies', 'Atlanta Hawks',
                                     'Houston Rockets', 'New Orleans Pelicans', 'Washington Wizards','Orlando Magic'],
	                      'Team 4': ['Detroit Pistons', 'San Antonio Spurs', 'Charlotte Hornets', 'Minnesota Timberwolves',
                                     'Cleveland Cavaliers', 'Sacramento Kings', 'Chicago Bulls']})

	#Create the wins table
	merged_wins = teams.merge(standings_df, left_on='Team 1', right_on='Team')
	merged_wins = merged_wins.rename(columns={"W": 'Team 1 Wins', 'L': 'Team 1 Losses', "Record": "Team 1 Record"})

	merged_wins = merged_wins.merge(standings_df, left_on='Team 2', right_on='Team')
	merged_wins = merged_wins.rename(columns={"W": 'Team 2 Wins', 'L': 'Team 2 Losses', "Record": "Team 2 Record"})

	merged_wins = merged_wins.merge(standings_df, left_on='Team 3', right_on='Team')
	merged_wins = merged_wins.rename(columns={"W": 'Team 3 Wins', 'L': 'Team 3 Losses', "Record": "Team 3 Record"})

	merged_wins = merged_wins.merge(standings_df, left_on='Team 4', right_on='Team')
	merged_wins = merged_wins.rename(columns={"W": 'Team 4 Wins', 'L': 'Team 4 Losses', "Record": "Team 4 Record"})

	merged_wins['Total Wins'] = merged_wins['Team 1 Wins'] + merged_wins['Team 2 Wins'] +\
								merged_wins['Team 3 Wins'] + merged_wins['Team 4 Wins']

	merged_wins['Win Percentage'] = round((merged_wins['Total Wins'])/
										  (merged_wins['Total Wins'] +
										   merged_wins['Team 1 Losses'] + merged_wins['Team 2 Losses'] +
										   merged_wins['Team 3 Losses'] + merged_wins['Team 4 Losses']), 3)
	merged_wins['Win Percentage'] = merged_wins['Win Percentage'].replace(np.nan, .000)

	merged_wins = merged_wins[['Team Name','Owner', 'Total Wins', 'Win Percentage',
							   'Team 1', 'Team 1 Record',
							   'Team 2', 'Team 2 Record',
							   'Team 3', 'Team 3 Record',
							   'Team 4',  'Team 4 Record']]

	#Apply Nebeyu penalty
	#merged_wins.iloc[0, merged_wins.columns.get_loc('Total Wins')] = (merged_wins.iloc[0, merged_wins.columns.get_loc('Total Wins')] - 5)

	#NBA Logos
	merged_wins['Team 1 Image'] = [os.path.join(app.config['nba_folder'],'bucks.png'),
								   os.path.join(app.config['nba_folder'],'heat.png'),
								   os.path.join(app.config['nba_folder'],'nets.png'),
								   os.path.join(app.config['nba_folder'],'celtics.png'),
								   os.path.join(app.config['nba_folder'],'lakers.png'),
								   os.path.join(app.config['nba_folder'],'clippers.png'),
								   os.path.join(app.config['nba_folder'],'nuggets.png')]

	merged_wins['Team 2 Image'] = [os.path.join(app.config['nba_folder'],'pacers.png'),
								   os.path.join(app.config['nba_folder'],'76ers.png'),
								   os.path.join(app.config['nba_folder'],'trail_blazers.png'),
								   os.path.join(app.config['nba_folder'],'raptors.png'),
								   os.path.join(app.config['nba_folder'],'suns.png'),
								   os.path.join(app.config['nba_folder'],'jazz.png'),
								   os.path.join(app.config['nba_folder'],'mavericks.png')]

	merged_wins['Team 3 Image'] = [os.path.join(app.config['nba_folder'],'warriors.png'),
								   os.path.join(app.config['nba_folder'],'grizzlies.png'),
								   os.path.join(app.config['nba_folder'],'hawks.png'),
								   os.path.join(app.config['nba_folder'],'rockets.png'),
								   os.path.join(app.config['nba_folder'],'pelicans.png'),
								   os.path.join(app.config['nba_folder'],'wizards.png'),
								   os.path.join(app.config['nba_folder'],'magic.png')]

	merged_wins['Team 4 Image'] = [os.path.join(app.config['nba_folder'],'pistons.png'),
								   os.path.join(app.config['nba_folder'],'spurs.png'),
								   os.path.join(app.config['nba_folder'],'hornets.png'),
								   os.path.join(app.config['nba_folder'],'timberwolves.png'),
								   os.path.join(app.config['nba_folder'],'cavaliers.png'),
								   os.path.join(app.config['nba_folder'],'kings.png'),
								   os.path.join(app.config['nba_folder'],'bulls.png')]

	merged_wins = merged_wins.sort_values(by=['Total Wins'], ascending = False)
	merged_wins.reset_index(drop=True, inplace=True)

	#Pass league standings to html
	return render_template('responsive_table.html',  team1_data = merged_wins.iloc[0].values,
	 									   team2_data = merged_wins.iloc[1].values,
	                                       team3_data = merged_wins.iloc[2].values, 
	                                       team4_data = merged_wins.iloc[3].values,
	                                       team5_data = merged_wins.iloc[4].values, 
	                                       team6_data = merged_wins.iloc[5].values,
	                                       team7_data = merged_wins.iloc[6].values)


@app.route('/tracker',methods=['GET'])
#Create monthly tracker
def tracker():
	if request.method == 'GET':

		# Get current wins

		# Scrape standings from basketball-reference
		stats_page = requests.get('https://www.basketball-reference.com/leagues/NBA_2021.html')
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

		# Add necessary columns to standings
		standings_df = western_conf_df.append(eastern_conf_df)

		# standings_df['Team'] = standings_df['Team'].str.extract('(.*)[(]')
		standings_df['Team'] = standings_df['Team'].astype(str)
		standings_df['Team'] = standings_df['Team'].str.replace("\([0-9]+\)", "")
		standings_df['Team'] = standings_df['Team'].str.strip()

		standings_df['W'] = standings_df['W'].replace(np.nan, 0)
		standings_df['L'] = standings_df['L'].replace(np.nan, 0)
		standings_df['W'] = standings_df["W"].round().astype(int)
		standings_df['L'] = standings_df["L"].round().astype(int)
		standings_df["Record"] = standings_df['W'].map(str) + "-" + standings_df['L'].map(str)

		# Set up the teams
		teams = pd.DataFrame({'Team Name': ['Team Nebeyu',
											'They all start with 0 wins',
											"Our friend is an alcoholic and it's troubling",
											"Sammy Ps AF1s Est. 2011",
											"Pre-pubescent toddler",
											"Did it",
											"Benjamin Bogdanovic"],
							  'Owner': [os.path.join(app.config['profiles_folder'], 'nebeyu.png'),
										os.path.join(app.config['profiles_folder'], 'phil.png'),
										os.path.join(app.config['profiles_folder'], 'fitz.png'),
										os.path.join(app.config['profiles_folder'], 'cepehr.png'),
										os.path.join(app.config['profiles_folder'], 'gabe.png'),
										os.path.join(app.config['profiles_folder'], 'young.png'),
										os.path.join(app.config['profiles_folder'], 'ben.png')],
							  'Team 1': ['Milwaukee Bucks', 'Miami Heat', 'Brooklyn Nets',
										 'Boston Celtics', 'Los Angeles Lakers', 'Los Angeles Clippers',
										 'Denver Nuggets'],
							  'Team 2': ['Indiana Pacers', 'Philadelphia 76ers', 'Portland Trail Blazers',
										 'Toronto Raptors', 'Phoenix Suns', 'Utah Jazz', 'Dallas Mavericks'],
							  'Team 3': ['Golden State Warriors', 'Memphis Grizzlies', 'Atlanta Hawks',
										 'Houston Rockets', 'New Orleans Pelicans', 'Washington Wizards',
										 'Orlando Magic'],
							  'Team 4': ['Detroit Pistons', 'San Antonio Spurs', 'Charlotte Hornets',
										 'Minnesota Timberwolves',
										 'Cleveland Cavaliers', 'Sacramento Kings', 'Chicago Bulls']})

		# Create the wins table
		merged_wins = teams.merge(standings_df, left_on='Team 1', right_on='Team')
		merged_wins = merged_wins.rename(columns={"W": 'Team 1 Wins', 'L': 'Team 1 Losses', "Record": "Team 1 Record"})

		merged_wins = merged_wins.merge(standings_df, left_on='Team 2', right_on='Team')
		merged_wins = merged_wins.rename(columns={"W": 'Team 2 Wins', 'L': 'Team 2 Losses', "Record": "Team 2 Record"})

		merged_wins = merged_wins.merge(standings_df, left_on='Team 3', right_on='Team')
		merged_wins = merged_wins.rename(columns={"W": 'Team 3 Wins', 'L': 'Team 3 Losses', "Record": "Team 3 Record"})

		merged_wins = merged_wins.merge(standings_df, left_on='Team 4', right_on='Team')
		merged_wins = merged_wins.rename(columns={"W": 'Team 4 Wins', 'L': 'Team 4 Losses', "Record": "Team 4 Record"})

		merged_wins['Total Wins'] = merged_wins['Team 1 Wins'] + merged_wins['Team 2 Wins'] + \
									merged_wins['Team 3 Wins'] + merged_wins['Team 4 Wins']

		merged_wins['Win Percentage'] = round((merged_wins['Total Wins']) /
											  (merged_wins['Total Wins'] +
											   merged_wins['Team 1 Losses'] + merged_wins['Team 2 Losses'] +
											   merged_wins['Team 3 Losses'] + merged_wins['Team 4 Losses']), 3)
		merged_wins['Win Percentage'] = merged_wins['Win Percentage'].replace(np.nan, .000)

		teams_standings = pd.DataFrame({'Team Name': ['Team Nebeyu',
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
						  'December Win %': merged_wins['Win Percentage']})

		teams_standings = teams_standings.sort_values(by=['December Win %'], ascending=False)
		teams_standings.reset_index(drop=True, inplace=True)

		return render_template('tracker_table.html',  team1_data = teams_standings.iloc[0].values,
	 									   team2_data = teams_standings.iloc[1].values,
	                                       team3_data = teams_standings.iloc[2].values,
	                                       team4_data = teams_standings.iloc[3].values,
	                                       team5_data = teams_standings.iloc[4].values,
	                                       team6_data = teams_standings.iloc[5].values,
	                                       team7_data = teams_standings.iloc[6].values)

# Debugger
if __name__ == "__main__":
    app.run(debug=True)









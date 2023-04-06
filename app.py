#Import
import os

#Import other stuff
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
#Caching imports
from flask_caching import Cache

#Set folder paths
logos_folder = os.path.join('static', 'nba_logos')
pics_folder = os.path.join('static', 'profiles')

#App setup
app = Flask(__name__)
app.config['nba_folder'] = logos_folder
app.config['profiles_folder'] = pics_folder

cache = Cache(app,config={'CACHE_TYPE': 'simple'})
app.secret_key = 'a;sldks;js?##s;kasjjdfjd'

#Define homepage
@app.route("/", methods=['GET'])
#Get the standings
def home():

	#Scrape standings from basketball-reference
	stats_page = requests.get('https://www.basketball-reference.com/leagues/NBA_2023.html')
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
	standings_df = pd.concat([eastern_conf_df, western_conf_df])

	standings_df['Team'] = standings_df['Team'].astype(str)
	standings_df['Team'] = standings_df['Team'].str.replace("\([0-9]+\)", "", regex=True)
	standings_df['Team'] = standings_df['Team'].str.replace("*", "", regex=True)
	standings_df['Team'] = standings_df['Team'].str.strip()

	standings_df['W'] = standings_df['W'].replace(np.nan, 0)
	standings_df['L'] = standings_df['L'].replace(np.nan, 0)
	standings_df['W'] = standings_df["W"].round().astype(int)
	standings_df['L'] = standings_df["L"].round().astype(int)
	standings_df["Record"] = standings_df['W'].map(str) + "-" + standings_df['L'].map(str)

	# Set up the teams
	teams = pd.DataFrame({'Team Name': ['Team Nebeyu', 
										'Team Phil', 
	                                    'Team Fitz', 
	                                    'Team Cepehr',
	                                    'Team Gabe',
	                                    'Team Young',
	                                    'Team Ben'],
	                      'Owner': [os.path.join(app.config['profiles_folder'],'nebeyu.png'),
									os.path.join(app.config['profiles_folder'],'phil.png'),
									os.path.join(app.config['profiles_folder'],'fitz.png'),
									os.path.join(app.config['profiles_folder'],'cepehr.png'),
									os.path.join(app.config['profiles_folder'],'gabe.png'),
									os.path.join(app.config['profiles_folder'],'young.png'),
									os.path.join(app.config['profiles_folder'],'ben.png')],
	                      'Team 1': ['Philadelphia 76ers', 'Golden State Warriors', 'Milwaukee Bucks',
	                      			  'Memphis Grizzlies','Boston Celtics', 'Los Angeles Clippers', 'Denver Nuggets'],
	                      'Team 2': ['Phoenix Suns', 'Brooklyn Nets', 'Atlanta Hawks',
                                     'Miami Heat', 'Toronto Raptors', 'Dallas Mavericks', 'Minnesota Timberwolves'],
	                      'Team 3': ['New York Knicks', 'Portland Trail Blazers', 'Los Angeles Lakers',
                                     'Sacramento Kings', 'Cleveland Cavaliers', 'New Orleans Pelicans','Chicago Bulls'],
	                      'Team 4': ['Washington Wizards', 'Detroit Pistons', 'Houston Rockets',
						   			 'Charlotte Hornets', 'Indiana Pacers', 'Utah Jazz', 'Orlando Magic']})

	#Create the wins table
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

	merged_wins['Win Percentage'] = round((merged_wins['Total Wins'])/(merged_wins['Total Wins'] + \
										   merged_wins['Team 1 Losses'] + merged_wins['Team 2 Losses'] +\
										   merged_wins['Team 3 Losses'] + merged_wins['Team 4 Losses']), 3)
	merged_wins['Win Percentage'] = merged_wins['Win Percentage'].replace(np.nan, .000)

	merged_wins = merged_wins[['Team Name','Owner', 'Total Wins', 'Win Percentage',
							   'Team 1', 'Team 1 Record',
							   'Team 2', 'Team 2 Record',
							   'Team 3', 'Team 3 Record',
							   'Team 4',  'Team 4 Record']]

	#NBA Logos
	merged_wins['Team 1 Image'] = [os.path.join(app.config['nba_folder'],'76ers.png'),
								   os.path.join(app.config['nba_folder'],'warriors.png'),
								   os.path.join(app.config['nba_folder'],'bucks.png'),
								   os.path.join(app.config['nba_folder'],'grizzlies.png'),
								   os.path.join(app.config['nba_folder'],'celtics.png'),
								   os.path.join(app.config['nba_folder'],'clippers.png'),
								   os.path.join(app.config['nba_folder'],'nuggets.png')]

	merged_wins['Team 2 Image'] = [os.path.join(app.config['nba_folder'],'suns.png'),
								   os.path.join(app.config['nba_folder'],'nets.png'),
								   os.path.join(app.config['nba_folder'],'hawks.png'),
								   os.path.join(app.config['nba_folder'],'heat.png'),
								   os.path.join(app.config['nba_folder'],'raptors.png'),
								   os.path.join(app.config['nba_folder'],'mavericks.png'),
								   os.path.join(app.config['nba_folder'],'timberwolves.png')]

	merged_wins['Team 3 Image'] = [os.path.join(app.config['nba_folder'],'knicks.png'),
								   os.path.join(app.config['nba_folder'],'trail_blazers.png'),
								   os.path.join(app.config['nba_folder'],'lakers.png'),
								   os.path.join(app.config['nba_folder'],'kings.png'),
								   os.path.join(app.config['nba_folder'],'cavaliers.png'),
								   os.path.join(app.config['nba_folder'],'pelicans.png'),
								   os.path.join(app.config['nba_folder'],'bulls.png')]

	merged_wins['Team 4 Image'] = [os.path.join(app.config['nba_folder'],'wizards.png'),
								   os.path.join(app.config['nba_folder'],'pistons.png'),
								   os.path.join(app.config['nba_folder'],'rockets.png'),
								   os.path.join(app.config['nba_folder'],'hornets.png'),
								   os.path.join(app.config['nba_folder'],'pacers.png'),
								   os.path.join(app.config['nba_folder'],'jazz.png'),
								   os.path.join(app.config['nba_folder'],'magic.png')]

	merged_wins = merged_wins.sort_values(by=['Total Wins', 'Win Percentage'], ascending = False)
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
		stats_page = requests.get('https://www.basketball-reference.com/leagues/NBA_2023.html')
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
		standings_df = pd.concat([western_conf_df, eastern_conf_df])

		standings_df['Team'] = standings_df['Team'].astype(str)
		standings_df['Team'] = standings_df['Team'].str.replace("\([0-9]+\)", "", regex=True)
		standings_df['Team'] = standings_df['Team'].str.replace("*", "", regex=True)
		standings_df['Team'] = standings_df['Team'].str.strip()

		standings_df['W'] = standings_df['W'].replace(np.nan, 0)
		standings_df['L'] = standings_df['L'].replace(np.nan, 0)
		standings_df['W'] = standings_df["W"].round().astype(int)
		standings_df['L'] = standings_df["L"].round().astype(int)
		standings_df["Record"] = standings_df['W'].map(str) + "-" + standings_df['L'].map(str)

		# Set up the teams
		teams = pd.DataFrame({'Team Name': ['Team Nebeyu',
											'Team Phil',
											"Team Fitz",
											"Team Cepehr",
											"Team Gabe",
											"Team Young",
											"Team Ben"],
							  'Owner': [os.path.join(app.config['profiles_folder'], 'nebeyu.png'),
										os.path.join(app.config['profiles_folder'], 'phil.png'),
										os.path.join(app.config['profiles_folder'], 'fitz.png'),
										os.path.join(app.config['profiles_folder'], 'cepehr.png'),
										os.path.join(app.config['profiles_folder'], 'gabe.png'),
										os.path.join(app.config['profiles_folder'], 'young.png'),
										os.path.join(app.config['profiles_folder'], 'ben.png')],
	                      'Team 1': ['Philadelphia 76ers', 'Golden State Warriors', 'Milwaukee Bucks',
	                      			  'Memphis Grizzlies','Boston Celtics', 'Los Angeles Clippers', 'Denver Nuggets'],
	                      'Team 2': ['Phoenix Suns', 'Brooklyn Nets', 'Atlanta Hawks',
                                     'Miami Heat', 'Toronto Raptors', 'Dallas Mavericks', 'Minnesota Timberwolves'],
	                      'Team 3': ['New York Knicks', 'Portland Trail Blazers', 'Los Angeles Lakers',
                                     'Sacramento Kings', 'Cleveland Cavaliers', 'New Orleans Pelicans','Chicago Bulls'],
	                      'Team 4': ['Washington Wizards', 'Detroit Pistons', 'Houston Rockets',
						   			 'Charlotte Hornets', 'Indiana Pacers', 'Utah Jazz', 'Orlando Magic'],
						  'October Wins': [15,12,12,11,16,16,12],
						  'October Losses': [12,16,15,16,11,11,16],
						  'November Wins': [33,27,28,28,39,33,27],
						  'November Losses': [27,35,28,29,20,28,31],
						  'December Wins': [28,32,25,31,30,35,29],
						  'December Losses': [31,25,35,28,30,27,30],
						  'January Wins': [34,23,30,34,29,24,37],
						  'January Losses': [23,32,31,26,33,36,23],
						  'February Wins': [27,16,22,22,28,18,25],
						  'February Losses': [16,28,20,21,16,24,21],
						  'March Wins': [35,21,34,36,32,27,30],
						  'March Losses': [28,42,29,27,27,30,28]})

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

		merged_wins['Total Losses'] = merged_wins['Team 1 Losses'] + merged_wins['Team 2 Losses'] + \
									merged_wins['Team 3 Losses'] + merged_wins['Team 4 Losses']

		merged_wins['October Win Percentage'] = round((merged_wins['October Wins']/(merged_wins['October Wins'] + merged_wins['October Losses'])), 3)
		merged_wins['October Win Percentage'] = merged_wins['October Win Percentage'].replace(np.nan, .000)

		merged_wins['November Win Percentage'] = round((merged_wins['November Wins']/(merged_wins['November Wins'] + merged_wins['November Losses'])), 3)
		merged_wins['November Win Percentage'] = merged_wins['November Win Percentage'].replace(np.nan, .000)

		merged_wins['December Win Percentage'] = round((merged_wins['December Wins']/(merged_wins['December Wins'] + merged_wins['December Losses'])), 3)
		merged_wins['December Win Percentage'] = merged_wins['December Win Percentage'].replace(np.nan, .000)

		merged_wins['January Win Percentage'] = round((merged_wins['January Wins']/(merged_wins['January Wins'] + merged_wins['January Losses'])), 3)
		merged_wins['January Win Percentage'] = merged_wins['January Win Percentage'].replace(np.nan, .000)

		merged_wins['February Win Percentage'] = round((merged_wins['February Wins']/(merged_wins['February Wins'] + merged_wins['February Losses'])), 3)
		merged_wins['February Win Percentage'] = merged_wins['February Win Percentage'].replace(np.nan, .000)

		merged_wins['March Win Percentage'] = round((merged_wins['March Wins']/(merged_wins['March Wins'] + merged_wins['March Losses'])), 3)
		merged_wins['March Win Percentage'] = merged_wins['March Win Percentage'].replace(np.nan, .000)

		april_wins = merged_wins['Total Wins'] - merged_wins['October Wins'] - merged_wins['November Wins'] - merged_wins['December Wins'] - merged_wins['January Wins'] - merged_wins['February Wins'] - merged_wins['March Wins']
		april_losses = merged_wins['Total Losses'] - merged_wins['October Losses'] - merged_wins['November Losses'] - merged_wins['December Losses'] - merged_wins['January Losses'] - merged_wins['February Losses'] - merged_wins['March Losses']

		merged_wins['April Win Percentage'] = round((april_wins/(april_wins + april_losses)), 3)
		merged_wins['April Win Percentage'] = merged_wins['April Win Percentage'].replace(np.nan, .000)

		# merged_wins['January Win Percentage'] = round((merged_wins['January Wins']/(merged_wins['January Wins'] + merged_wins['January Losses'])), 3)
		# merged_wins['January Win Percentage'] = merged_wins['January Win Percentage'].replace(np.nan, .000)

		# merged_wins['February Win Percentage'] = round((merged_wins['February Wins']/(merged_wins['February Wins'] + merged_wins['February Losses'])), 3)
		# merged_wins['February Win Percentage'] = merged_wins['February Win Percentage'].replace(np.nan, .000)

		# merged_wins['March Win Percentage'] = round((merged_wins['March Wins']/(merged_wins['March Wins'] + merged_wins['March Losses'])), 3)
		# merged_wins['March Win Percentage'] = merged_wins['March Win Percentage'].replace(np.nan, .000)

		# merged_wins['April Win Percentage'] = round((merged_wins['Total Wins'] - merged_wins['October Wins'] - 
		# 	merged_wins['November Wins'] - merged_wins['December Wins'] - merged_wins['January Wins'] - merged_wins['February Wins'] -
		# 	merged_wins['March Wins'])/((merged_wins['Total Wins'] - merged_wins['October Wins'] - merged_wins['November Wins'] - 
		# 												merged_wins['December Wins'] - merged_wins['January Wins'] - merged_wins['February Wins'] -
		# 												merged_wins['March Wins'] +
		# 											 (merged_wins['Total Losses'] - merged_wins['October Losses'] - 
		# 											 	merged_wins['November Losses'] - merged_wins['December Losses'] - merged_wins['January Losses'] -
		# 											 	merged_wins['February Losses'] - merged_wins['March Losses']))), 3)
		# merged_wins['April Win Percentage'] = merged_wins['April Win Percentage'].replace(np.nan, .000)

		teams_standings = pd.DataFrame({'Team Name': ['Team Nebeyu',
											'Team Phil',
											"Team Fitz",
											"Team Cepehr",
											"Team Gabe",
											"Team Young",
											"Team Ben"],
										'Owner': [os.path.join(app.config['profiles_folder'], 'nebeyu.png'),
												  os.path.join(app.config['profiles_folder'], 'phil.png'),
												  os.path.join(app.config['profiles_folder'], 'fitz.png'),
												  os.path.join(app.config['profiles_folder'], 'cepehr.png'),
												  os.path.join(app.config['profiles_folder'], 'gabe.png'),
												  os.path.join(app.config['profiles_folder'], 'young.png'),
												  os.path.join(app.config['profiles_folder'], 'ben.png')],
										'October Win %': merged_wins['October Win Percentage'],
										'November Win %': merged_wins['November Win Percentage'],
										'December Win %': merged_wins['December Win Percentage'],
										'January Win %': merged_wins['January Win Percentage'],
										'February Win %': merged_wins['February Win Percentage'],
										'March Win %': merged_wins['March Win Percentage'],
										'April Win %': merged_wins['April Win Percentage']
										})

		teams_standings = teams_standings.sort_values(by=['March Win %'], ascending=False)
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









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
app.secret_key = b'?\x8c\x1eg#/|\x13\xe4\xc8;\xc3\x0e\x13\xe9$'
app.config['MYSQL_DATABASE_HOST'] = 'mysql-instance1.cyxrf7jrt6gm.us-east-2.rds.amazonaws.com'
app.config['MYSQL_DATABASE_USER'] = 'hindesn'
app.config['MYSQL_DATABASE_PASSWORD'] = 'minnie4us'
app.config['MYSQL_DATABASE_DB'] = 'cis550hpps'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql = MySQL()
mysql.init_app(app)


from flask import Flask
import sqlite3
import os
import json

app = Flask(__name__)

@app.route('/')
def index():
  return 'welcome! please go to url /food or /meals 😋 '
  
@app.route('/food')
def get_food():
  cur.execute("SELECT id, name, calories FROM food")
  food_results = cur.fetchall()
  return json.dumps({'food:' : food_results})

@app.route('/meals')
def get_meals():
  cur.execute("SELECT id, name FROM meals")
  meal_results = cur.fetchall()
  return  json.dumps({'meals:' : meal_results})

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

con  = db_connect()
cur = con.cursor()

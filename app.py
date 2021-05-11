from flask import Flask
from flask import jsonify, request
import sqlite3
import os
import json

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

app = Flask(__name__)

@app.route('/')
def index():
  return 'welcome! please go to /day-summary to see summary of today or /food to see all foods or /meals to se all meals 😋 '
 
@app.route('/food')
def get_food():
  con  = db_connect()
  cur = con.cursor()
  cur.execute("SELECT id, name, calories FROM food")
  food_results = cur .fetchall()
  return json.dumps({'food:' : food_results})

@app.route('/meals')
def get_meals():
  con  = db_connect()
  cur = con.cursor()
  cur.execute("SELECT id, name FROM meals")
  meal_results = cur.fetchall()
  return  json.dumps({'meals:' : meal_results})

@app.route('/day-summary')
def get_day_summary():
  resp = None
  try:
    date = request.args.get('date')
    if date:
      print('date finns')
      conn = db_connect()
      cursor = conn.cursor()
      cursor.execute("SELECT m.name, f.name, ce.meal_id, ce.food_id, ce.quantity, f.calories FROM calendar_entries as ce LEFT JOIN meals m on ce.meal_id=m.id LEFT JOIN food f on ce.food_id=f.id WHERE ce.date='" + date +"'")
      row = cursor.fetchall()
      resp = jsonify(row)
      entries = []
      for li in row:
        isMeal = True if li[0] != None else False
        if isMeal:
          cursor.execute("SELECT mf.food_id, f.calories, mf.quantity FROM meal_food as mf LEFT JOIN food f on mf.food_id=f.id WHERE meal_id='" + str(li[2]) + "'")
          meals = cursor.fetchall()
          kcalCount = 0
          for ingredient in meals:
            kcalCount += 0.01 * ingredient[1] * ingredient[2]
            print('adding ' +str(kcalCount)+  ' calories to meal: ' + li[0]  )
          
        entries.append({
          'name': li[0] if isMeal else li[1], 
          'id':li[2] if isMeal else li[3], 
          'quantity':li[4], 
          'caloriesPer100':li[5],
          'calories': 0.01 * li[4] * li[5] if li[5]!=None else kcalCount
        })

     
      
    else:
      entries = "validation failed"
    
  except Exception as e:
    print('asdf')
    print(e)
  
  return json.dumps(entries)
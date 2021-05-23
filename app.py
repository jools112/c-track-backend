from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import json
sqlite3.paramstyle = 'named'


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')

def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con

app = Flask(__name__)
CORS(app)

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

@app.route('/search')
def get_search_results():
  status = 200
  try: 
    query = request.args.get('query')
    print('user searched for: ' + query)

    if query:
      conn = db_connect()
      cursor = conn.cursor()
      cursor.execute("SELECT name, id, calories FROM food WHERE name LIKE :query", {"query": '%' + query + '%'})
      food_hits = cursor.fetchall()
      cursor.execute("SELECT name, id FROM meals WHERE name LIKE :query", {"query":'%' + query + '%'})
      meal_hits = cursor.fetchall()
      results = []

      for food in food_hits[0:5]: #TODO test new endpoint
        results.append({'name' : food[0], 'id' : food[1],'calories' : food[2], 'type' : 'food'})
        
      for meal in meal_hits[0:5]:
        results.append({'name': meal[0], 'id':meal[1],'calories' : 567, 'type': 'meal'}) #TODO calculate calories like in daysummary meal
    
    else: 
      results = []
      

  except Exception as e:
    print(e)

  return jsonify(results)

@app.route('/day-summary', methods = ['POST', 'GET'])
def day_summary():
  if request.method == 'GET':
    resp = None
    try:
      date = request.args.get('date')
      if date:
        conn = db_connect()
        cursor = conn.cursor()
        cursor.execute("SELECT m.name, f.name, ce.meal_id, ce.food_id, ce.quantity, f.calories FROM calendar_entries as ce LEFT JOIN meals m on ce.meal_id=m.id LEFT JOIN food f on ce.food_id=f.id WHERE ce.date=:date", {"date":date})
        row = cursor.fetchall()
        resp = jsonify(row)
        entries = []
        for li in row:
          isMeal = True if li[0] != None else False
          if isMeal:
            cursor.execute("SELECT mf.food_id, f.calories, mf.quantity FROM meal_food as mf LEFT JOIN food f on mf.food_id=f.id WHERE meal_id=:mealId", {"mealId":str(li[2])})
            meals = cursor.fetchall()
            kcalCount = 0
            weightCount = 0
            for ingredient in meals:
              kcalCount += 0.01 * ingredient[1] * ingredient[2]
              weightCount +=  ingredient[2]
              #print('adding ' +str(kcalCount)+  ' calories to meal: ' + li[0] + ' with total weight '+ str(weightCount) + ' and calories per 100g: ' + str(100*kcalCount/weightCount) )
        
          entries.append({
            'name': li[0] if isMeal else li[1], 
            'id':li[2] if isMeal else li[3], 
            'quantity':li[4], 
            'caloriesPer100':  round(100*kcalCount/weightCount) if isMeal else li[5],
            'calories': round(0.01 * li[4] * li[5]) if li[5]!=None else round(kcalCount)
          })
        
      else:
        entries = "validation failed"
 
    except Exception as e:
      print(e)
    return jsonify(entries)

  elif request.method == 'POST':
    data = request.json
    conn = db_connect()
    cursor = conn.cursor()
    response = ''
    status = 200

    if data['type'] == 'food':
      food_count = cursor.execute("SELECT COUNT(id) FROM food WHERE id=" + str(data['id'])).fetchall()
      if food_count[0][0]:
        cursor.execute("INSERT INTO calendar_entries ( food_id, date, quantity) VALUES (?,?,?)", 
        ( data['id'], data['date'], data['quantity']))
      else:
        status = 400

    elif data['type'] == 'meal':
      meal_count = cursor.execute("SELECT COUNT(id) FROM meals WHERE id=" + str(data['id'])).fetchall()
      if meal_count[0][0]:
        cursor.execute("INSERT INTO calendar_entries ( meal_id, date, quantity) VALUES (?,?,?)", 
        ( data['id'], data['date'], data['quantity']))
      else: 
        status = 400

    else:
      print('Invalid entry type: ', data['type'])
      status = 400
    conn.commit()
      
    return jsonify(response), status
     
    
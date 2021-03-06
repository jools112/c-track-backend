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

@app.route('/measurements')
def get_measurements():
  con = db_connect()
  cur = con.cursor()
  cur.execute("SELECT date, weight FROM measurements")
  measurements_results = cur.fetchall()
  return json.dumps({'measurements: ': measurements_results})

@app.route('/search')
def get_search_results():
  status = 200
  try: 
    query = request.args.get('query')

    if query:
      conn = db_connect()
      cursor = conn.cursor()
      cursor.execute("SELECT name, id, calories FROM food WHERE name LIKE :query", {"query": '%' + query + '%'})
      food_hits = cursor.fetchall()
      cursor.execute("SELECT name, id FROM meals WHERE name LIKE :query", {"query":'%' + query + '%'})
      meal_hits = cursor.fetchall()
      results = []

      for food in food_hits[0:5]:
        results.append({'name' : food[0], 'id' : food[1],'calories' : food[2], 'type' : 'food'})
        
      for meal in meal_hits[0:5]: # must calculate calorie content of all ingredients in meal
        cursor.execute("SELECT mf.food_id, f.calories, mf.quantity FROM meal_food as mf LEFT JOIN food f on mf.food_id=f.id WHERE meal_id=:mealId", {"mealId":str(meal[1])})
        selectedMeals = cursor.fetchall()
        kcalCount = 0
        weightCount = 0
        for ingredient in selectedMeals:
          kcalCount +=   ingredient[1] * ingredient[2]
          weightCount +=  ingredient[2]
        results.append({'name': meal[0], 'id':meal[1],'calories' : round((1/weightCount)*kcalCount), 'type': 'meal'}) 
    
    else: 
      results = []
      

  except Exception as e:
    print(e)

  return jsonify(results)

@app.route('/day-summary', methods = ['POST', 'GET', 'PATCH', 'DELETE'])
def day_summary():

  def get_entry(meal_name, food_name, calendar_meal_id, calendar_id, quantity, calories):
    """ 
      indata: mealname?, foodname?, calendar_mealid?, calendarid, quantity, calories?    
      bestäm om meal eller food
      om meal: hämta alla ingredienser och räkna
      i båda fallen, hämta info och skapa entry
    """

    isMeal = True if meal_name != None else False
    if isMeal:
      cursor.execute("SELECT mf.food_id, f.calories, mf.quantity FROM meal_food as mf LEFT JOIN food f on mf.food_id=f.id WHERE meal_id=:mealId", {"mealId":str(calendar_meal_id)})
      meals = cursor.fetchall()
      kcalCount = 0
      weightCount = 0
      for ingredient in meals:
        kcalCount += ingredient[1] * 0.01 * ingredient[2]
        weightCount +=  0.01 * ingredient[2]
      kcalPer100Meal = kcalCount/weightCount

    entry = {
      'name': meal_name if isMeal else food_name, 
      'id':calendar_id, 
      'quantity':quantity, 
      'caloriesPer100':  round(kcalPer100Meal) if isMeal else calories,
      'calories': round(0.01*kcalPer100Meal*quantity) if isMeal else round(0.01 * quantity * calories)
    }
    return entry
  
  data = request.json
  conn = db_connect()
  cursor = conn.cursor()
  
  if request.method == 'POST':
    response = ''
    status = 200

    if data['type'] == 'food':
      food_count = cursor.execute("SELECT COUNT(id) FROM food WHERE id=" + str(data['id'])).fetchall()
      if food_count[0][0]:
        cursor.execute("INSERT INTO calendar_entries ( food_id, date, quantity) VALUES (?,?,?)", 
        ( data['id'], data['date'], data['quantity']))
      else:
        status = 400

    elif data['type'] == 'meal': #calculate the calories!!
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

  elif request.method == 'GET':
      resp = None
      try:
        date = request.args.get('date')
        if date:         
          cursor.execute("SELECT m.name, f.name, ce.meal_id, ce.id, ce.quantity, f.calories FROM calendar_entries as ce LEFT JOIN meals m on ce.meal_id=m.id LEFT JOIN food f on ce.food_id=f.id WHERE ce.date=:date", {"date":date})
          row = cursor.fetchall()
          resp = jsonify(row)
          entries = []
          for li in row:
            entries.append(get_entry(li[0], li[1], li[2], li[3], li[4], li[5]))
          
        else:
          entries = "GET validation failed"
  
      except Exception as e:
        print(e)
      return jsonify(entries)

  elif request.method == 'PATCH':
    entry = ''
    status = 200

    try:
      date = request.args.get('date')
      entry_id = request.args.get('id')
      quantity = data['quantity']
      cursor.execute("UPDATE calendar_entries SET quantity=" + str(quantity) + " WHERE id=" + str(entry_id))
      conn.commit()
      cursor.execute("SELECT m.name, f.name, ce.meal_id, f.calories FROM calendar_entries as ce LEFT JOIN meals m on ce.meal_id=m.id LEFT JOIN food f on ce.food_id=f.id WHERE ce.id=:id", {"id":str(entry_id)})
      fetched = cursor.fetchall()
      entry_data = fetched[0]
      entry = get_entry(entry_data[0], entry_data[1], entry_data[2], entry_id, quantity, entry_data[3])
   
    except Exception as e:
      print(e)

    return jsonify(entry)

  elif request.method == 'DELETE':

    cursor = conn.cursor()
    response = ''
    status = 200
   
    cursor.execute("DELETE FROM calendar_entries WHERE id=" + str(data['id'])) 
    conn.commit()
    return jsonify(response), status
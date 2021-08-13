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
  

  if request.method == 'POST':
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
          conn = db_connect()
          cursor = conn.cursor()
          cursor.execute("SELECT m.name, f.name, ce.meal_id, ce.id, ce.quantity, f.calories FROM calendar_entries as ce LEFT JOIN meals m on ce.meal_id=m.id LEFT JOIN food f on ce.food_id=f.id WHERE ce.date=:date", {"date":date})
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
                kcalCount += ingredient[1] * 0.01 * ingredient[2]
                weightCount +=  0.01 * ingredient[2]
              kcalPer100Meal = kcalCount/weightCount

            entries.append({
              'name': li[0] if isMeal else li[1], 
              'id':li[3], 
              'quantity':li[4], 
              'caloriesPer100':  round(kcalPer100Meal) if isMeal else li[5],
              'calories': round(0.01 * li[4] * li[5]) if li[5]!=None else round(0.01*kcalPer100Meal*li[4])
            })
          
        else:
          entries = "GET validation failed"
  
      except Exception as e:
        print(e)
      return jsonify(entries)

  elif request.method == 'PATCH':
    response = ''
    status = 200

    try:
      data = request.json
      date = request.args.get('date')
      entry_id = request.args.get('id')
      quantity = data['quantity']
      conn = db_connect()
      cursor = conn.cursor()
      #schtuff = cursor.fetchall()
      print('date and id : ' + date + ' and ' + entry_id + ' and data: ' + str(quantity))

      cursor.execute("UPDATE calendar_entries SET quantity=" + str(quantity) + " WHERE id=" + str(entry_id))
      conn.commit()
    except Exception as e:
      print(e)

    return jsonify(response)

  elif request.method == 'DELETE':
    data = request.json
    conn = db_connect()
    cursor = conn.cursor()
    response = ''
    status = 200
   
    cursor.execute("DELETE FROM calendar_entries WHERE id=" + str(data['id'])) 
    conn.commit()
    return jsonify(response), status
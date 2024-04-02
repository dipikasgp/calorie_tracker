from flask import Flask, render_template, g, request, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)


def connect_db():
    sql = sqlite3.connect('C:/Dipika/Study/calorie_tracker/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite3'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=['POST', 'GET'])
def index():
    db = get_db()
    if request.method == 'POST':
        date = request.form['date']

        dt = datetime.strptime(date, '%Y-%m-%d')
        database_date = datetime.strftime(dt, '%Y%m%d')

        db.execute('insert into log_date (entry_date) values(?) order by entry_date DESC', [database_date])
        db.commit()
    cur = db.execute('select entry_date from log_date')
    results = cur.fetchall()

    pretty_res = []
    for i in results:
        single_date = {}
        d = datetime.strptime(str(i['entry_date']), '%Y%m%d')
        single_date['entry_date'] = datetime.strftime(d, '%B %d, %Y')
        pretty_res.append(single_date)
    return render_template('home.html', results=pretty_res)


@app.route('/view/<date>', methods=['POST', 'GET'])
def view(date):
    db = get_db()
    # if request.method == 'POST':

    cur = db.execute('select entry_date from log_date where entry_date = ?', [date])
    result = cur.fetchone()

    d = datetime.strptime(str(result['entry_date']), '%Y%m%d')
    pretty_date = datetime.strftime(d, '%B %d, %Y')

    cur = db.execute('select id, name from food')
    food_list = cur.fetchall()

    return render_template('day.html', date=pretty_date, food_result=food_list)


@app.route('/food', methods=['GET', 'POST'])
def food():
    db = get_db()
    if request.method == 'POST':
        name = request.form['food-name']
        protein = int(request.form['protein'])
        carbohydrates = int(request.form['carbohydrates'])
        fat = int(request.form['fat'])
        calories = (protein * 4) + (carbohydrates * 4) + (fat * 9)
        db.execute("insert into food (name, protein, carbohydrates, fat, calories)\
                    values(?,?,?,?,?)", [name, protein, carbohydrates, fat, calories])
        db.commit()

    cur = db.execute('select name,protein, carbohydrates, fat, calories from food')
    results = cur.fetchall()
    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run()

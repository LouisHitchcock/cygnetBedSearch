
from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('bed_availability.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    r = cursor.fetchall()
    conn.close()
    return (r[0] if r else None) if one else r

@app.route('/api/data')
def get_data():
    male_wards = query_db("SELECT * FROM wards WHERE gender = 'male'")
    female_wards = query_db("SELECT * FROM wards WHERE gender = 'female'")
    return jsonify({'male_wards': male_wards, 'female_wards': female_wards})

@app.route('/api/change_log')
def get_change_log():
    change_log = query_db("SELECT * FROM changes")
    return jsonify(change_log)

if __name__ == '__main__':
    app.run()

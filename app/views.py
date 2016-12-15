import flask
from app import app

@app.route('/')
def index():
  return '<h1>MOCMON Usage Report</h1>'

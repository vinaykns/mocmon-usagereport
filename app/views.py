import flask
from app import app
from .forms import DateForm
import os
import sys
import datetime
import json
import affi
from .calculation import calculation

@app.route('/', methods=['POST', 'GET'])
def index():
  form = DateForm()
  if flask.request.method == 'POST':
    if form.validate_on_submit():

      start = form.start_date.data
      end = form.end_date.data
      results1 = calculation(start,end)
      return flask.render_template('results.html', start=start, end=end, results=results1)
    else:
     flask.abort(500)
  else:
    return flask.render_template('index.html', form=form)

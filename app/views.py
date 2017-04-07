import flask
from app import app
from .forms import DateForm
import os
import sys
import datetime
import json
import affi
import pdb 

@app.route('/', methods=['POST', 'GET'])
def index():
  form = DateForm()
  if flask.request.method == 'POST':
    if form.validate_on_submit():

      start = form.start_date.data
      end = form.end_date.data
      from calculation1 import calculation
      results1 = calculation(start,end)
      total_projects = {}
      projects = results1.pop('Aggregation_Affiliations')
      total_projects['Total'] = projects
      return flask.render_template('results1.html', start=start, end=end, results=results1, total=total_projects)
    else:
     flask.abort(500)
  else:
    return flask.render_template('index.html', form=form)



@app.route('/users')
def users():

  class totalusers:
      def __init__(self):
          self.helo = "hello"

      def calculation2(self):
          from openstack_calculation import evaluation
          self.results2 = evaluation(self)

  B = totalusers()
  B.calculation2()
  affiliation_users = {}

  for affiliation in B.results2.viewkeys():
    affiliation_users[affiliation] = len(B.results2[affiliation])
     

  return flask.render_template('results2.html', results=affiliation_users)

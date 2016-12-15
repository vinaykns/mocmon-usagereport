import flask
from app import app
from .forms import DateForm

@app.route('/', methods=['POST', 'GET'])
def index():
  form = DateForm()
  if flask.request.method == 'POST':
    if form.validate_on_submit():
      start = form.start_date.data.strftime('%x')
      end = form.end_date.data.strftime('%x')
      return flask.render_template('results.html', start=start, end=end)
    else:
     flask.abort(500)
  else:
    return flask.render_template('index.html', form=form)

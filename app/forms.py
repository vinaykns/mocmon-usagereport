import flask_wtf
import wtforms

class DateForm(flask_wtf.Form):
  start_date = wtforms.DateField('Start Date', format='%m/%d/%Y', validators=[wtforms.validators.DataRequired()])
  end_date = wtforms.DateField('End Date', format='%m/%d/%Y', validators=[wtforms.validators.DataRequired()])
  submit = wtforms.SubmitField('Generate Report')

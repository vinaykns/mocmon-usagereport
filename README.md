# mocmon-usagereport
To get the resource-allocation statistics of MOC, please clone by:
git clone https://github.com/vinaykns/mocmon-usagereport.git

This being a flask application one should have a flask virtual environment to execute the application.

1.To install flask on your local instance -- pip install virtualenv

2.Give a name to the virtual environment -- virtualenv flask
  
Then flask can be activated by source ~{PRESENT_DIR}/bin/activate

Then install the packages required for the flask application to run, in this case we need:
1. pip install flask
2. pip install flask_wtf

Then finally run python main.py to open a web page listening at port 8888.(localhost:8888 on your webbrowser.)

1. To get the allocation statistics per Organisation select the dates from the web page to display the output.
2. To get the user statistics per organisation go to path localhost:8888/users 

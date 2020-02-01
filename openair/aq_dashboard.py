from flask import Flask
from openaq import API,OpenAQ
import openaq
from flask_sqlalchemy import SQLAlchemy


APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(APP)

class Record(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    datetime = DB.Column(DB.String(25))
    value = DB.Column(DB.Float, nullable=False)

    def __repr__(self):
        return '<Time : {}>-----<Value: {}>'.format(self.datetime,self.value)


@APP.route('/')
def root():
    """Base view."""
    potentially_risky = Record.query.filter(Record.value >= 10.0).all()
    return  str(potentially_risky)
    
   
def data(city='Los Angeles', parameter='pm25'):
    api = openaq.OpenAQ()
    status, body = api.measurements(city=city, parameter=parameter)
    values = []
    for result in body['results']:
        utc_datatime = result['date']['utc']
        value = result['value']
        values.append((utc_datatime, value))
    return values

       

@APP.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    def data(city='Los Angeles', parameter='pm25'):
        api = openaq.OpenAQ()
        status, body = api.measurements(city=city, parameter=parameter)
        values = []
        for result in body['results']:
            utc_datatime = result['date']['utc']
            value = result['value']
            values.append((utc_datatime, value))
        return values
    DB.drop_all()
    DB.create_all()
    # TODO Get data from OpenAQ, make Record objects with it, and add to db
    data = data()
    for x in data:
        record = Record(datetime=x[0], value=x[1])
        DB.session.add(record)

   
    DB.session.commit()
    return 'Data refreshed!'



if __name__ == '__main__':
    app.run(debug=True)

     

   



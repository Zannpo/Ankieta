import os
from flask import Flask,request,render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, RadioField, BooleanField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
'sqlite:///' + os.path.join(basedir, 'covidData.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app) 
migrate = Migrate(app,db)

app.config['SECRET_KEY'] = 'pa$$w0d'

bootstrap = Bootstrap(app)

class CovidCases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    pesel = db.Column(db.String(9), nullable = False)
    symptoms = db.Column(db.String(100), nullable = False)
    lengthOfIlness = db.Column(db.String(3), nullable=False)
    medicine = db.Column(db.String(30), nullable = False)
    flights = db.Column(db.String(20))   
    hospitalisation = db.Column(db.String(5), nullable = False)

    def __init__(self, name, surname, pesel, symptoms, lengthOfIlness, medicine, flights, hospitalisation):
        self.name = name
        self.surname = surname
        self.pesel = pesel
        self.symptoms = symptoms
        self.lengthOfIlness = lengthOfIlness
        self.medicine = medicine
        self.flights = flights
        self.hospitalisation = hospitalisation

@app.route('/')
def main():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

class NameForm(FlaskForm):
    name = StringField('Imię',validators=[DataRequired(), Length(max=50)])
    surname = StringField('Nazwisko', validators=[DataRequired(), Length(max=50)])
    pesel = StringField('PESEL', validators=[DataRequired(), Length(min=9,max=9)])
    symptoms = StringField('Wymień dotyczące ciebie objawy choroby', validators=[DataRequired(), Length(max=100)])
    lengthOfIlness = IntegerField('Podaj ilość dni przebytej choroby', validators=[DataRequired()])
    medicine = StringField('Wypisz przyjmowane leki', validators=[DataRequired(), Length(max=30)])
    flights = StringField('Czy przed zachorowaniem byłeś w innym kraju? Jeśli tak podaj w jakim, jeśli nie zostaw puste pole', validators=[Length(max=20)])
    hospitalisation = RadioField('Czy byłeś hospitalizowany?',choices=[(True,'Byłem hospitalizowany'),(False,'Nie byłem hospitalizowany')], validators=[DataRequired()])
    submit = SubmitField('Wyślij')

class NameForm2(FlaskForm):
    id = IntegerField('Podaj numer id danych, które chcesz zmienić')
    name = StringField('Imię',validators=[DataRequired(), Length(max=50)])
    surname = StringField('Nazwisko', validators=[DataRequired(), Length(max=50)])
    pesel = StringField('PESEL', validators=[DataRequired(), Length(min=9,max=9)])
    symptoms = StringField('Wymień dotyczące ciebie objawy choroby', validators=[DataRequired(), Length(max=100)])
    lengthOfIlness = IntegerField('Podaj ilość dni przebytej choroby', validators=[DataRequired()])
    medicine = StringField('Wypisz przyjmowane leki', validators=[DataRequired(), Length(max=30)])
    flights = StringField('Czy przed zachorowaniem byłeś w innym kraju? Jeśli tak podaj w jakim, jeśli nie zostaw puste pole', validators=[Length(max=20)])
    hospitalisation = RadioField('Czy byłeś hospitalizowany?',choices=[(True,'Byłem hospitalizowany'),(False,'Nie byłem hospitalizowany')], validators=[DataRequired()])
    submit2 = SubmitField('Zatwierdź')

@app.route('/form', methods=['GET', 'POST'])
def form():
    name = None
    surname = None
    pesel = None
    symptoms = None
    lengthOfIlness = None
    medicine = None
    hospitalisation = None    
    form = NameForm()

    if form.validate_on_submit():
       name = request.form['name']
       surname = request.form['surname']
       pesel = request.form['pesel']
       symptoms = request.form['symptoms']
       lengthOfIlness = request.form['lengthOfIlness']
       medicine = request.form['medicine']
       flights = request.form['flights']
       hospitalisation = request.form['hospitalisation']
       patientData = CovidCases(name, surname, pesel, symptoms, lengthOfIlness, medicine, flights, hospitalisation)
       db.session.add(patientData)
       db.session.commit()   
       return render_template('form.html', form = form)
    else:
        message = 'Wystąpił błąd'
        return render_template('form.html', form = form, message=message)
    
@app.route('/edit', methods=['GET', 'POST'])
def edit():     
    form = NameForm2()    

    if form.validate_on_submit():
          id = request.form['id']       
          person = CovidCases.query.filter_by(id=id).first()
          if person is None:              
              return render_template('error.html', form = form)     
          person.name = request.form['name']
          person.surname = request.form['surname']
          person.pesel = request.form['pesel']
          person.symptoms = request.form['symptoms']
          person.lengthOfIlness = request.form['lengthOfIlness']
          person.medicine = request.form['medicine']
          person.flights = request.form['flights']
          person.hospitalisation = request.form['hospitalisation']
          db.session.commit()   
          return render_template('edit.html', form = form)    
    else:
        message = 'Wystąpił błąd'
        return render_template('form.html', form = form, message=message)


@app.route('/results')
def results():    
    number = 0
    listOfPeople = CovidCases.query.order_by(CovidCases.id)
    numberOfHospitalisation = CovidCases.query.filter(CovidCases.hospitalisation == 'True')
    for i in numberOfHospitalisation:
        number = number + 1

    return render_template("results.html", listOfPeople = listOfPeople, number = number)


if __name__ == "__main__":
    app.run(debug=True)
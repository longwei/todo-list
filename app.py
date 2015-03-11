__author__ = 'longwei'


from flask import Flask
from flask import render_template, request
from flask_bootstrap import Bootstrap
import os

#forms
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

class IdeaForm(Form):
    idea_name = StringField('idea', validators=[DataRequired()])
    submit_button = SubmitField('Add a idea')


app = Flask(__name__)
# in a real app, these should be configured through Flask-Appconfig
app.config['SECRET_KEY'] = 'devkey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)


class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idea_name = db.Column(db.String(140))

    def __init__(self, idea):
        self.idea_name = idea

    def __repr__(self):
        return '<Idea %r>' % self.id

db.create_all()

Bootstrap(app)
@app.route("/", methods=["GET", "POST"])
def index():
    form = IdeaForm()
    if request.method == 'POST' and form.validate():
        print "post"
        idea = Idea(form.idea_name.data)
        db.session.add(idea)
        db.session.commit()
    list_of_ideas = Idea.query
    return render_template("index.html", form = form, list_of_ideas= list_of_ideas)


@app.route('/hello', methods=["GET"])
def hello():
    return "hello world";

@app.route('/hello', methods=["POST"])
def yes():
    print "ack"
    return "hello world";


if __name__ == "__main__":
    app.run(debug=True)

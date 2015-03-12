__author__ = 'longwei'


from flask import Flask
from flask import render_template, request
from flask_bootstrap import Bootstrap
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
import os

#forms
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy

class IdeaForm(Form):
    idea_name = StringField('Idea', validators=[DataRequired()])
    submit_button = SubmitField('Add idea')


app = Flask(__name__)
# in a real app, these should be configured through Flask-Appconfig
app.config['SECRET_KEY'] = 'devkey'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_CHANGE_EMAIL'] = False
app.config['SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL'] = False

#create db connection
db = SQLAlchemy(app)

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


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
    list_of_ideas = Idea.query.all()
    #current_user is magically passed in
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

__author__ = 'longwei'


from flask import Flask
from flask.ext.login import current_user
from flask import render_template, request, url_for, flash
from flask_bootstrap import Bootstrap
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
import os
import wtf_helpers

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
app.config['SECURITY_FLASH_MESSAGES'] = True

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
    ideas = db.relationship('Idea', backref='user', lazy='dynamic')

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

class Idea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    idea_name = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, idea, user):
        self.idea_name = idea
        self.user_id = user.id

    def __repr__(self):
        return '<Idea %r>' % self.id

db.create_all()

Bootstrap(app)
wtf_helpers.add_helpers(app)
@app.route("/")
def index():
    users = User.query
    return render_template("index.html", users=users)
    #
    # form = IdeaForm()
    # if request.method == 'POST' and form.validate():
    #     print "post"
    #     idea = Idea(form.idea_name.data)
    #     db.session.add(idea)
    #     db.session.commit()
    #

    # list_of_ideas = Idea.query.all()
    # #current_user is magically passed in
    # return render_template("index.html", form=form, list_of_ideas=list_of_ideas)


@app.route("/ideas/<user_email>", methods = ["GET", "POST"])
def ideas(user_email):
    user = User.query.filter_by(email=user_email).first_or_404()

    if user == current_user:
        form = IdeaForm()
    else:
        form = None

    if form and form.validate_on_submit():
        idea = Idea(form.idea_name.data, user)
        db.session.add(idea)
        db.session.commit()
        flash("Idea was added successfully", "success")
    list_of_ideas = user.ideas
    return render_template("ideas.html", form=form,
                               list_of_ideas=list_of_ideas, user_email=user_email)

@app.route("/site-map")
def site_map():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)
    return render_template('sitemap.html', result=output)
    # links is now a list of url, endpoint tuples

if __name__ == "__main__":
    app.run(debug=True)

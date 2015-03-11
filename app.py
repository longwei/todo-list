__author__ = 'longwei'


from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap


#forms
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class IdeaForm(Form):
    idea = StringField('idea', validators=[DataRequired()])
    submit_button = SubmitField('Add a idea')


app = Flask(__name__)
# in a real app, these should be configured through Flask-Appconfig
app.config['SECRET_KEY'] = 'devkey'
# app.config['RECAPTCHA_PUBLIC_KEY'] = \
#         '6Lfol9cSAAAAADAkodaYl9wvQCwBMr3qGR_PPHcw'
Bootstrap(app)


@app.route("/", methods = ["GET", "POST"])
def hello():
    form = IdeaForm()
    submitted_idea = "No idea yet"
    if form.validate_on_submit():
        submitted_idea = form.idea.data
    return render_template("index.html", form = form,
                           submitted_idea=submitted_idea)

if __name__ == "__main__":
    app.run(debug=True)

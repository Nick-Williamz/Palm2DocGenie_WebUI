from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class ChatForm(FlaskForm):
    message = StringField('Ask a Question', validators=[DataRequired()])
    submit = SubmitField('Submit')
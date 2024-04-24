from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# ------------- WTF - FORM -------------
class UploadForm(FlaskForm):
    text_input = StringField('Text Input', validators=[DataRequired()])
    image = FileField('Image File or URL', validators=[
        FileAllowed(['jpg', 'png', 'gif'], 'Images only!')
    ])

class TxtUploadForm(FlaskForm):
    txt_file = FileField('Upload Text File', validators=[
        FileRequired(),
        FileAllowed(['txt'], 'Text Files only!')
    ])
    submit = SubmitField('Submit')
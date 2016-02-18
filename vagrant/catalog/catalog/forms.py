from flask_wtf import Form
from wtforms import StringField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed


class CategoryForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=250)])


class ItemForm(Form):
    name = StringField('Name', validators=[DataRequired(), Length(max=250)])
    description = TextAreaField('Description', validators=[Length(max=1000)])
    image = FileField('Image', validators=[FileAllowed(['jpeg', 'jpg', 'png', 'gif', 'bmp'], 'File must be an image.')])
    category = SelectField('Category', choices=None, coerce=int)

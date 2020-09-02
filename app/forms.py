from flask_wtf import FlaskForm
from wtforms import StringField, TextField, PasswordField, SubmitField, RadioField, IntegerField, HiddenField, BooleanField, FormField, SelectMultipleField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, InputRequired
from wtforms.form import BaseForm, Form
from wtforms import validators, ValidationError, widgets


WTF_CSRF_SECRET_KEY = '###############'

class LoginForm(FlaskForm):
	
	email = TextField("Email", validators=[InputRequired("Please enter your email"), Email("Please enter an email")])
	password = PasswordField("Password", validators=[DataRequired("Enter your password")])
	submit = SubmitField("Login")

class SignUp(FlaskForm):
	
	name = TextField("Name", validators=[InputRequired(message = "Please enter your name")])
	email = TextField("Email", validators=[InputRequired(message = "Please enter your email"), Email("Please enter an email")])
	password = PasswordField("Password", validators=[InputRequired(message = "Enter your password"), Length(min = 4, message = "Minimum password length 4")])
	password_confirm = PasswordField("Password Confirm", validators=[InputRequired(message = "Enter your password"), EqualTo('password', message = "Passwords must match")])
	submit = SubmitField("Sign Up")


class SheetInfo(FlaskForm):
	
	sheet_name = TextField("Sheet Name", validators=[InputRequired(message = "Please enter sheet name")])
	starting_row = IntegerField("Starting Row", validators=[InputRequired(message = "Please enter starting row")])
	link_col = IntegerField("Link Column", validators=[InputRequired(message = "Please enter link column")])
	title_col = IntegerField("Title Column", validators=[InputRequired(message = "Please enter title column")])
	sheet_id = TextField("Sheet Link", validators=[InputRequired(message = "Please enter sheet link")])
	submit = SubmitField("Submit Sheet Info")

class Classification(FlaskForm):

	agriculture = BooleanField(label='Agriculture')

	building = BooleanField(label='Building')

	cultural = BooleanField(label='Cultural Aspect')
	cultural_sub1 = TextField()

	infastructure = BooleanField(label='Infastructure')

	livestock = BooleanField(label='Livestock')

	landscape = BooleanField(label='Landscape')
	landscape_sub_alpine = BooleanField(label='Sub Alpine')
	landscape_alpine_meadow = BooleanField(label='Alpine Meadow')
	landscape_alpine_scrub = BooleanField(label='Alpine Scrub')
	landscape_other_bool = BooleanField(label="Other")
	landscape_other = TextField(label='Other')
	landscape_sub2 = RadioField(choices=['Correctly', 'Incorrectly', 'No ID', 'Other'])
	landscape_sub2_free = TextField(label='Other')
	
	plant = BooleanField(label='Plant')
	plant_sub1_answer = HiddenField(label="Does user ID plants?")
	plant_sub2_answer = HiddenField(label="Is user ID correct?")
	plant_sub3_answer = TextField(label='User identified species / genus')
	plant_sub4_answer = HiddenField(label="Are individual plants / flowers visible?")
	plant_sub5_answer = TextField(label="Plant Species / Genus")
	plant_sub6_answer = HiddenField(label="Is Plant a black , red, watch list species")
	plant_sub7_answer = HiddenField(label="Was user aware of these categories?")
	plant_sub8_answer = TextField(label='Plant Tags')

	people = BooleanField(label='People')
	people_sub1 = RadioField(choices=['Yes', 'No', 'IDK'])

	pet = BooleanField(label='Pet')
	
	wildlife = BooleanField(label='Wildlife')
	
	water = BooleanField(label='Water Feature')
	water_stream = BooleanField(label='Stream / River')
	water_lake = BooleanField(label='Lake / Pond')
	water_waterfall = BooleanField(label='Waterfall')
	water_coastal = BooleanField(label='Coastal')
	water_other_bool = BooleanField(label='Other')
	water_other = TextField(label='Other')

	water_response = HiddenField(label='water_response')

	weather = BooleanField(label="Weather")
	weather_sub1 = TextField(label='What type of weather?')

	recreational = BooleanField(label='Recreational')

	english = BooleanField(label='English')
	italian = BooleanField(label='Italian')
	german = BooleanField(label='German')
	french = BooleanField(label='French')
	icelandic = BooleanField(label='Icelandic')
	no_lang = BooleanField(label='None')
	idk_lang = BooleanField(label='IDK')
	other_lang_bool = BooleanField(label='Other')
	other_lang = TextField(label='Other: ')

	comment = TextAreaField(label='Comments:')

	Next = SubmitField("Next")
	Previous = SubmitField("Previous")

	go_to_row = IntegerField("Target row")

# Testing
"""
class ThisForm():

	def add_bool(name, label):
		setattr(ThisForm, name, BooleanField(label=label))
	pass

def test():

	fields = ['Calendrier', 'Commentaire', 'Dessin', 'Ex-libris', 'Gravure', 'test']

	def form_from_fields(fields):
			def create_form(prefix='', **kwargs):
				form = BaseForm(fields, prefix=prefix)
				form.process(**kwargs)
				return form
			return create_form

	return form_from_fields([(field, BooleanField(field)) for field in fields])

class MainFormOne(FlaskForm):

	#list_checkbox = FormField(form_from_fields([(field, BooleanField(field)) for field in fields]))
	list_checkbox = FormField(test())
"""








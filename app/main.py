from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from . import db
from . import integration
from .forms import SheetInfo, Classification, ThisForm, MainFormOne
from .model import Sheet, User


main = Blueprint('main', __name__)

main.secret_key = '#############'
WTF_CSRF_SECRET_KEY = '###############'


@main.route('/')
def index():
	return render_template('index.html')

@main.route('/about')
def about():
	return render_template('about.html')


@main.route('/landing', methods=['GET', 'POST'])
@login_required
def landing():

	sheets = Sheet.query.filter_by(user_id = current_user.id).all()

	
	form = SheetInfo()

	return render_template('landing.html', name = current_user.name.title(), sheets = sheets, form=form, alright=False, alright_message='')



@main.route('/deletesheet/<ids>', methods=['GET'])
@login_required
def deleteSheet(ids):

	request_sheet = Sheet.query.filter_by(id = ids).first()

	if current_user.id == request_sheet.user_id:

		Sheet.query.filter_by(id=ids).delete()

		db.session.commit()

		return redirect(url_for('main.landing'))

	else:

		return redirect(url_for ('main.landing'))

	
@main.route('/addsheet', methods=['GET', 'POST'])
@login_required
def newSheet():

	form = SheetInfo()

	if form.validate_on_submit():
		print("Form 1 Validate on Summit")


		if form.validate() == False:

			flash('All fields are required.')
			
			return render_template('landing.html', form=form, name=current_user.name.title(), sheets=sheets, alright = False, alright_message='')
			
		name = str(request.form.get('sheet_name'))
		link_col = int(request.form.get('link_col'))
		title_col = int(request.form.get('title_col'))
		row = int(request.form.get('starting_row'))
		sheet_id = str(request.form.get('sheet_id'))

		new_sheet = Sheet(sheet_name = name, sheet_title_col = title_col, 
			sheet_link_col = link_col, user_id = int(current_user.id), starting_row = row, sheet_id = sheet_id)

		db.session.add(new_sheet)
		db.session.commit()

		print(current_user.sheets)

		
		return render_template('landing.html', form = form, alright= True, alright_message = 'Form Saved', 
		name=current_user.name.title(), sheets=Sheet.query.filter_by(user_id = current_user.id).all())

	return render_template('landing.html', form = form, alright= False, alright_message = '', 
		name=current_user.name.title(), sheets=Sheet.query.filter_by(user_id = current_user.id).all())
	

# Pull vars from selected sheet object. Set to session
@main.route('/classify/<ids>')
@login_required
def getClassifySheet(ids):

	def get_name():

		name = current_user.name.title().split()

		initials = ''

		for names in name:

			initials += str(names[0])

		return initials

	request_sheet = Sheet.query.filter_by(id = ids).first()

	if current_user.id == request_sheet.user_id:

		target = Sheet.query.filter_by(id=ids).first()

		session['sheet_name'] = str(target.sheet_name)
		session['sheet_id'] = str(target.sheet_id)
		session['link_column'] = int(target.sheet_link_col)
		session['title_column'] = int(target.sheet_title_col)
		
		session['starting_row'] = int(target.starting_row)
		session['current_row'] = session['starting_row']
		session['reviewer'] = get_name()
		print(session['current_row'])

		# Activate API Connection
		try:
			client = integration.activateConnection()

		except:
			flash('Invalid Auth Credentials')
			return redirect(url_for('main.landing'))


		
		# Receive Sheet Object
		try:
			sheet = integration.connectToSheet(client)

		except:
			
			flash('Title Not Found')
			return redirect(url_for('main.landing'))

		# Get All Col Data
		integration.getColData(ids, sheet)

		
		return redirect(url_for("main.classify"))

	else:
		flash('You are not authorized')
		return redirect(url_for ('main.landing'))



@main.route('/classify', methods=['GET', 'POST'])
@login_required
def classify():

	form = Classification()

	# POST METHOD
	if request.method == 'POST':

		print("NEW POST")
		results = request.form
		print(results)

		if 'Next' in request.form:

			integration.interpret(results)
			integration.rowChange(True)

		elif 'Previous' in request.form:
		
			integration.rowChange(False)

		elif 'go_to_row' in request.form:

			session['current_row'] = int(request.form.get('go_to_row')) 

		return redirect(url_for('main.classify'))


	new_link, pic_title = integration.getNextInfo()
		
	return render_template('redoClassify.html', pic_title = pic_title, 
		link = new_link, form = form, row = session['current_row'])


# Testing
"""
@main.route('/template', methods=['GET', 'POST'])
@login_required
def template():

	#list_name = ('Test1', 'Test2', 'Test3')
	#list_apply = list()
	#name = list()

	#for i in range(len(list_name)):
	#	ThisForm.add_bool(list_name[i], list_name[i])
	#	list_apply.append(list_name[i])
	#	i+=1

	#ThisForm.add_bool('teste', 'teste')



	fields = ['Calendrier', 'Commentaire', 'Dessin', 'Ex-libris', 'Gravure', 'test']
	
	

	form = MainFormOne()
	
	list(form.list_checkbox)
	print(*form.list_checkbox, sep='\n')

	

	#form = ThisForm()
	#print(dir(form))

	#for i in dir(form):

	#	if i[0] != '_':
	#		name.append(i)
	#		print(i)

	#print(form)

	return render_template('test-add.html', form=form)
"""



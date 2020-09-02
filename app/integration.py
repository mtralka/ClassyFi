from flask import session
import gspread, sys, os
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
import pickle
import time


scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

schema = ['plant', 'water']

COL_SCHEMA = (
        "reviewer", 'comments', "subject", 'lang', "plant_sub1", "plant_sub2",
        "plant_sub3",
        "plant_sub4", "plant_sub5", "plant_sub6", "plant_sub7", "plant_sub8",
        "landscape_sub1", "landscape_sub2", "people_sub1", "water_type",
        "weather_sub1", "cultural_sub1")

global cred, client, sheet

def activateConnection():
	
	
	#creds = ServiceAccountCredentials.from_json_keyfile_name('CREDS.json', scope)
	
	creds = Credentials.from_service_account_file('CREDS.json', scopes=scope)
	client = gspread.authorize(creds)

	print('Auth Done')
	
	return client
	

def connectToSheet(client):
	
	# sheet = client.open(str(session['sheet_name'])).sheet1
	# sheet = client.open(str(session['sheet_id'])).sheet1
	sheet = client.open_by_url(session['sheet_id']).sheet1
	
	print('Connection to Sheet')
	
	return sheet

def getNextInfo():
	start_time = time.time()
	# Recreate pickle ID from session
	link_pickle = session['link_pickle'] 
	title_pickle = session['title_pickle']

	# Load pickles
	with open(link_pickle, 'rb') as f:
		links = pickle.load(f)

	with open(title_pickle, 'rb') as f:
		titles = pickle.load(f)

	# Find matching link and title
	image_link = links[int(session['current_row']) - 1]
	title = titles[int(session['current_row']) - 1]

	print(time.time() - start_time)
	
	return image_link, title


def deletePickle():

	# Recreate pickle ID from session
	
	link_pickle = session['link_pickle'] 
	title_pickle = session['title_pickle']
	

	if os.path.exists(link_pickle):
		os.remove(link_pickle)
	

	if os.path.exists(title_pickle):
		os.remove(title_pickle)
	

def getColData(ids, sheet):

	# Pull Link Col from session
	linkCol = sheet.col_values(int(session['link_column']))
	titleCol = sheet.col_values(int(session['title_column']))

	# Create pickle ID
	link_pickle = str(ids) + '_link'
	title_pickle = str(ids) + '_title'

	# Store pickle ID
	session['link_pickle'] = link_pickle
	session['title_pickle'] = title_pickle

	# Dump Pickles
	with open(link_pickle, 'wb') as f:
		pickle.dump(linkCol, f)

		f.close()

	with open(title_pickle, 'wb') as f:
		pickle.dump(titleCol, f)

		f.close()

	
def rowChange(next_item):

	#print(f'current{getCurrentRow()}')
	current = int(session['current_row'])

	if next_item:
		session['current_row'] = current + 1
	else: 
		session['current_row'] = current - 1

def writeInput(header, input_message, sheet):
	
	modifying_col = int(schema.index(header)) + int(session['link_column']) + 1
	existing_message = sheet.cell(int(session['current_row']), modifying_col).value

	if len(str(existing_message)) > 0:
		message = f'{existing_message} | {input_message}'
	else:
		message = input_message

	sheet.update_cell(int(session['current_row']), modifying_col, message)



def interpret(results):
	"""
	COL_SCHEMA = (
        "Reviewer", 'Post Comments', "Subject", 'Languages', "Does User ID Plant", "Is ID Correct",
        "User Defined Plant Species",
        "Are Individual Plant Species Visible?", "Plant Species / Genus", "Are Flowers Visible?",
        "Black / Watch / Red List?", "Were Users Aware?", "What Tags are Used?",
        "Which Landscape is Visible?", "How does the user ID the landscape?", "Is it a selfie?", "Water Type",
        "Weather Type", "Cultural Aspect")
	"""
	

	def get_existing(heading):

		message = str(sheet.cell( session['current_row'] , int(COL_SCHEMA.index(heading)) + int(session['link_column']) + 1).value )
		
		return message
	
	def is_reviewed():
		existing = get_existing('reviewer')

		if len(existing) > 0:

			return True
		else:
			return False



	def write_cultural():

		if reviewed:
			message = get_existing('cultural_sub1')
			message += ' | '
		else:
			message = ''

		if len(results['cultural_sub1']) > 0:

			message += results['cultural_sub1']

		sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('cultural_sub1') + int(session['link_column']) + 1) , message)

	def write_landscape():

		landscape_dict = { 'landscape_sub_alpine' : 'subalpine', 'landscape_alpine_meadow' : 'alpine meadow', 'landscape_alpine_scrub' : 'alpine scrub'}

		if reviewed:
			message = get_existing('landscape_sub1')
			message += ' | '

			user_id = get_existing('landscape_sub2')
			user_id += ' | '

		else:
			message = ''
			user_id = ''

		for landscape in landscape_dict.keys():

			if landscape in results:

				message += landscape_dict[landscape] + ', '

		
		if 'landscape_other_bool' in results and results['landscape_other_bool']:

			message += results['landscape_other']
		

		if len(message) > 1:
			message = message.strip()

			if message[-1] == ',':
				message = message[:-1]

			sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('landscape_sub1') + int(session['link_column']) + 1) , message)


		# User landscape ID
		if 'landscape_sub2' in results:

			if results['landscape_sub2'] != 'Other':

				user_id += results['landscape_sub2']

				
			elif results['landscape_sub2'] == 'Other':

				user_id += results['landscape_sub2_free']

		sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('landscape_sub2') + int(session['link_column']) + 1) , user_id)

	def write_plant():

		PLANT_SUB = ("plant_sub1", "plant_sub2","plant_sub3",
        "plant_sub4", "plant_sub5", "plant_sub6", "plant_sub7", "plant_sub8")

		for sub in PLANT_SUB:

			if reviewed:
				message = get_existing(sub)
				message += ' | '
			else:
				message = ''

			results_key = str(sub) + '_answer'

			message += results[results_key]

			sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index(sub) + int(session['link_column']) + 1) , message)

	def write_people():

		if reviewed:
			message = get_existing('people_sub1')
			message += ' | '
		else:
			message = ''

		message += results['people_sub1']

		sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('people_sub1') + int(session['link_column']) + 1) , message)

	def write_water():

		water_dict = {'water_stream' : 'stream / river' , 'water_lake' : 'lake / pond' , 'water_waterfall' : 'waterfall' , 'water_coastal' : 'coastal'}

		if reviewed:
			message = get_existing('water_type')
			message += ' | '
		else:
			message = ''

		for types in water_dict.keys():

			if types in results:

				message += water_dict[types] + ', '

		if 'water_other_bool' in results and results['water_other_bool'] == 'y':

			message += results['water_other']

		if len(message) > 1:
			message = message.strip()

			if message[-1] == ',':
				message = message[:-1]

			sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('water_type') + int(session['link_column']) + 1) , message)

	def write_weather():
		
		if reviewed:
			message = get_existing('weather_sub1')
			message += ' | '
		else:
			message = ''

		if len(results['weather_sub1']) > 0:

			message += results['weather_sub1']

		sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('weather_sub1') + int(session['link_column']) + 1) , message)

	def write_subject():

		SUBJECT = ('agriculture', 'building', 'cultural', 'infastructure', 'livestock', 'landscape', 'plant', 'people', 'pet', 'wildlife', 'water', 'weather', 'recreational')

		if reviewed:
			message = get_existing('subject')
			message += ' | '
		else:
			message = ''


		for subjects in SUBJECT:
		
			if subjects in results:

				message += subjects + ', '

				if subjects == 'cultural':
					write_cultural()

				if subjects == 'landscape':
					write_landscape()

				if subjects == 'plant':
					write_plant()
				
				if subjects == 'people':
					write_people()

				if subjects == 'water':
					write_water()

				if subjects == 'weather':
					write_weather()

		if len(message) > 1:
			message = message.strip()

			if message[-1] == ',':
				message = message[:-1]

			sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('subject') + int(session['link_column']) + 1) , message)
		

	def write_lang():

		LANG_DICT = { 'english' : 'english' , 'italian' : 'italian' , 'german' : 'german' , 'french' : 'french' , 'icelandic' : 'icelandic' , 'no_lang' : 'none' , 'idk_lang' : 
		'idk'} 

		if reviewed:
			message = get_existing('lang')
			message += ' | '
		else:
			message = ''

		for langs in LANG_DICT.keys():
		
			if langs in results:

				message += LANG_DICT[langs] + ', '

		if 'other_lang_bool' in results and results['other_lang_bool'] == 'y':

			message += results['other_lang']

		if len(message) > 1:
			message = message.strip()

			if message[-1] == ',':
				message = message[:-1]

		sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('lang') + int(session['link_column']) + 1) , message)

	def write_comment():

		if reviewed:
			message = get_existing('comments')
			message += ' | '
		else:
			message = ''

		if len(results['comment']) > 0:

			message += results['comment']

		sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('comments') + int(session['link_column']) + 1) , message)

	def write_reviewer():

		if reviewed:
			message = get_existing('reviewer')
			message += ' | '
		else:
			message = ''

		message += session['reviewer']

		sheet.update_cell(session['current_row'] , int(COL_SCHEMA.index('reviewer') + int(session['link_column']) + 1) , message)


	print('Trigger Connection')
	start_time = time.time()
	sheet = connectToSheet(activateConnection())
	print(start_time - time.time())

	reviewed = is_reviewed()

	write_subject()
	write_lang()
	write_comment()

	write_reviewer()
	




	
	











	"""
	if "people" in results:
		print("people alert")

		if 'selfie':
			if results['selfie'] == 'Yes':
				print("Confirmed Yes")
			elif results['selfie'] == 'IDK':
				print("Confirmed IDK")
			elif results['selfie'] == 'No':
				print("Confirmed No")
			else:
				pass

	if "water" in results:

		print("We have watta")

		if 'water_lake' in results:

			print("Lake Pond")

		if 'water_waterfall' in results:

			print("Waterfall")
			
		if 'water_coastal' in results:
			
			print("Coastal Water")

		if 'water_stream' in results:

			print("Stream River")

		if len(str(results['water_other'])) > 0:
			
			print(str(results['water_other']))

		# Add to Sheet "Water Type"
		# Add to subject list


	if 'pet' in results:
			print("Pet Alert")
"""
"""
	for i in xlist:
		if str(i) in results:
			#
			# Add to list of subject
			#

		else:
			# Do nothign

	for i in resultsL
		if str(i) in subject_list:
			#
			# Add to Affimr Subject list
			#
		elif str(i) in lang_list
			#
			# Add to Affirm subject list
			#

	# Update Worksheet SUBJECT cell with all of subject list
	# Update worksheet LANG cell with all of list
"""

# Define as List
""""
	people = BooleanField(label='People')
	pet = BooleanField(label='Pet')
	livestock = BooleanField(label='Livestock')
	wildlife = BooleanField(label='Wildlife')
	plant = BooleanField(label='Plant')
	landscape = BooleanField(label='Landscape')
	water = BooleanField(label='Water Feature')
	recreational = BooleanField(label='Recreational')
	building = BooleanField(label='Building')
	infastructure = BooleanField(label='Infastructure')
	cultural = BooleanField(label='Cultural Aspect')
	agriculture = BooleanField(label='Agriculture')

	english = BooleanField(label='English')
	italian = BooleanField(label='Italian')
	german = BooleanField(label='German')
	french = BooleanField(label='French')
	icelandic = BooleanField(label='Icelandic')
	no_lang = BooleanField(label='None')
	idk_lang = BooleanField(label='IDK')
	other_lang = TextField(label='Other: ')
"""


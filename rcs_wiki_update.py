from datetime import datetime
import os, sys
import praw
import time
import pymssql
import requests
import ConfigParser

Config = ConfigParser.ConfigParser()
Config.read('/home/pi/rcs/sqlconfig.ini')
DatabaseName = Config.get('SectionOne', 'database')
DB_USERNAME = Config.get('SectionOne', 'username')
DB_PASSWORD = Config.get('SectionOne', 'password')
DB_HOST = Config.get('SectionOne', 'server')
API_KEY = Config.get('SectionTwo', 'apikey')

SUBREDDIT = 'coc_oak'
APP_NAME = "Clash of Clans Clan Wiki Page Updater"
BotName = 'CoC Bot'
APP_VERS = '1.2.0'
LAST_REFRESH = 0 # Last time the oAth Refresh Key was grabbed
SleepTime = 10800 # = 3 hours
API_URL = 'https://api.clashofclans.com/v1/clans/%23'
WIKI_PAGE = 'official_reddit_clan_system'
PAGE_CONTENT = ''
Headers = {'Accept':'application/json','Authorization':'Bearer ' + API_KEY}

def UpdateWikiPage(SUBREDDIT, WIKI_PAGE, PAGE_CONTENT):

	try:
		# Get existing wiki page data
		content = r.get_wiki_page(SUBREDDIT, WIKI_PAGE).content_md

		# Competitive Clans
		PAGE_CONTENT = ''
		start_marker = '[](#compStart)'
		end_marker = '[](#compEnd)'

		# Build the table
		cur.execute("SELECT clanName, subReddit, clanTag, clanLevel, members, warFreq, socMedia, notes, feeder FROM rcs_data WHERE classification='comp' ORDER BY clanName")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Clan&nbsp;Tag | Lvl | Members | War&nbsp;Frequency | Social&nbsp;Media | Notes | Feeder/Other\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-'

		for item in fetched:

			# Set proper War Frequenct Text
			if str(item[5]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[5]) == 'always':
				WarFreqText = 'Always'
			elif str(item[5]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[5]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[5]) == 'never':
				WarFreqText = 'Rarely'

			# Set proper Social Media
			if item[6] == 'None':
				socMedia = ''
			else:
				socMedia = item[6]

			# Set proper Notes
			if item[7] == 'None':
				clanNotes = ''
			else:
				clanNotes = item[7]
				
			# Set proper Feeder info
			if item[8] == 'None':
				feeder = ''
			else:
				feeder = '[See Below](https://www.reddit.com/r/RedditClanSystem/wiki/rcs_list_test#wiki_feeders.2Fassociated.2Fprospective)'

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[1]) + ') | [#' + str(item[2]) + '](https://www.clashofstats.com/clans/' + item[0].replace(' ', '-') + '-' + str(item[2]) + '/members) | ' + ' | ' + str(item[3]) + ' | ' + str(item[4]) + '/50 | ' + WarFreqText + ' | ' + socMedia + ' | ' + clanNotes + ' | ' + feeder

		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))


		# Social Clans

		PAGE_CONTENT = ''
		start_marker = '[](#socStart)'
		end_marker = '[](#socEnd)'

		# Build the table
		cur.execute("SELECT clanName, subReddit, clanTag, clanLevel, members, warFreq, socMedia, notes, feeder FROM rcs_data WHERE classification='social' ORDER BY clanName")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Total&nbsp;members | Clan&nbsp;Tag | Leader&nbsp;Name | Requirements | Archer&nbsp;Level | War&nbsp;Frequency | Status | War&nbsp;Wins\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-|-'

		for item in fetched:

			# Set proper War Frequenct Text
			if str(item[5]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[5]) == 'always':
				WarFreqText = 'Always'
			elif str(item[5]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[5]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[5]) == 'never':
				WarFreqText = 'Rarely'

			# Set proper Social Media
			if item[6] == 'None':
				socMedia = ''
			else:
				socMedia = item[6]

			# Set proper Notes
			if item[7] == 'None':
				clanNotes = ''
			else:
				clanNotes = item[7]
				
			# Set proper Feeder info
			if item[8] == 'None':
				feeder = ''
			else:
				feeder = '[See Below](https://www.reddit.com/r/RedditClanSystem/wiki/rcs_list_test#wiki_feeders.2Fassociated.2Fprospective)'

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[1]) + ') | [#' + str(item[2]) + '](https://www.clashofstats.com/clans/' + item[0].replace(' ', '-') + '-' + str(item[2]) + '/members) | ' + ' | ' + str(item[3]) + ' | ' + str(item[4]) + '/50 | ' + WarFreqText + ' | ' + socMedia + ' | ' + clanNotes + ' | ' + feeder
				
		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))

		# General Clans

		PAGE_CONTENT = ''
		start_marker = '[](#genStart)'
		end_marker = '[](#genEnd)'

		# Build the table
		cur.execute("SELECT clanName, subReddit, clanTag, clanLevel, members, warFreq, socMedia, notes, feeder FROM rcs_data WHERE classification='gen' ORDER BY clanName")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Total&nbsp;members | Clan&nbsp;Tag | Leader&nbsp;Name | Requirements | Archer&nbsp;Level | War&nbsp;Frequency | Status | War&nbsp;Wins\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-|-'

		for item in fetched:

			# Set proper War Frequenct Text
			if str(item[5]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[5]) == 'always':
				WarFreqText = 'Always'
			elif str(item[5]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[5]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[5]) == 'never':
				WarFreqText = 'Rarely'

			# Set proper Social Media
			if item[6] == 'None':
				socMedia = ''
			else:
				socMedia = item[6]

			# Set proper Notes
			if item[7] == 'None':
				clanNotes = ''
			else:
				clanNotes = item[7]
				
			# Set proper Feeder info
			if item[8] == 'None':
				feeder = ''
			else:
				feeder = '[See Below](https://www.reddit.com/r/RedditClanSystem/wiki/rcs_list_test#wiki_feeders.2Fassociated.2Fprospective)'

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[1]) + ') | [#' + str(item[2]) + '](https://www.clashofstats.com/clans/' + item[0].replace(' ', '-') + '-' + str(item[2]) + '/members) | ' + ' | ' + str(item[3]) + ' | ' + str(item[4]) + '/50 | ' + WarFreqText + ' | ' + socMedia + ' | ' + clanNotes + ' | ' + feeder

		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))

		# War Farming Clans
		
		PAGE_CONTENT = ''
		start_marker = '[](#wfStart)'
		end_marker = '[](#wfEnd)'

		# Build the table
		cur.execute("SELECT clanName, subReddit, clanTag, clanLevel, members, warFreq, socMedia, notes, feeder FROM rcs_data WHERE classification='warFarm' ORDER BY clanName")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Total&nbsp;members | Clan&nbsp;Tag | Leader&nbsp;Name | Requirements | Archer&nbsp;Level | War&nbsp;Frequency | Status | War&nbsp;Wins\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-|-'

		for item in fetched:

			# Set proper War Frequenct Text
			if str(item[5]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[5]) == 'always':
				WarFreqText = 'Always'
			elif str(item[5]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[5]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[5]) == 'never':
				WarFreqText = 'Rarely'

			# Set proper Social Media
			if item[6] == 'None':
				socMedia = ''
			else:
				socMedia = item[6]

			# Set proper Notes
			if item[7] == 'None':
				clanNotes = ''
			else:
				clanNotes = item[7]
				
			# Set proper Feeder info
			if item[8] == 'None':
				feeder = ''
			else:
				feeder = '[See Below](https://www.reddit.com/r/RedditClanSystem/wiki/rcs_list_test#wiki_feeders.2Fassociated.2Fprospective)'

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[1]) + ') | [#' + str(item[2]) + '](https://www.clashofstats.com/clans/' + item[0].replace(' ', '-') + '-' + str(item[2]) + '/members) | ' + ' | ' + str(item[3]) + ' | ' + str(item[4]) + '/50 | ' + WarFreqText + ' | ' + socMedia + ' | ' + clanNotes + ' | ' + feeder

		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))

		try:
			r.edit_wiki_page(SUBREDDIT, WIKI_PAGE, content, reason="Updating Clan Tracking Wikipage")
		except Exception:
			print("Wiki page update for {} FAILED".format(SUBREDDIT))
			
		# Feeder Clans
		
		PAGE_CONTENT = ''
		start_marker = '[](#feederStart)'
		end_marker = '[](#feederEnd)'

		# Build the table
		# I am cheating and using feeder for Home Clan, socMedia for Type, and clanLeader for contact
		cur.execute("SELECT feeder, clanName, clanTag, clanLevel, socMedia, members, clanLeader, leaderReddit, notes FROM rcs_data WHERE classification='feeder' ORDER BY feeder")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Home&nbsp;Clan | Clan&nbsp;Name | Clan&nbsp;Tag | Lvl | Type | Members | Contact | Notes\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-'

		for item in fetched:
			
			# Set Contact and Reddit username
			contact = '(' + item[6] + ')[/u/' + item[7]

			# Set proper Notes
			if item[8] == 'None':
				clanNotes = ''
			else:
				clanNotes = item[8]

			PAGE_CONTENT += item[0].replace(' ', '&nbsp;') | item[1].replace(' ', '&nbsp;') + ' | [#' + str(item[2]) + '](https://www.clashofstats.com/clans/' + item[1].replace(' ', '-') + '-' + str(item[2]) + '/members) | ' + str(item[3]) + ' | ' + item[4] + ' | ' + str(item[5]) + '/50 | ' + notes

		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))

		try:
			r.edit_wiki_page(SUBREDDIT, WIKI_PAGE, content, reason="Updating Clan Tracking Wikipage")
		except Exception:
			print("Wiki page update for {} FAILED".format(SUBREDDIT))			


	except Exception:
		print('General Update Wiki Page Error')

def UpdateDatabase():
	try:
		cur.execute('SELECT clantag FROM rcs_data')
		fetched = cur.fetchall()

		for item in fetched:
			clanTag = item[0]

			clandata = requests.get(API_URL + clantag).json()

			clanName = clandata['name']
			clanLevel = clandata['clanLevel']
			warFreq = clandata['warFrequency']
			members = clandata['members']
			
			mem = json.loads(clandata['memberList'])
			for role in mem:
				if role == 'leader':
					clanLeader = mem['name']

			# compare clan leader and report to council-chat if different
			# compare clan level and report to rcs-glocal-chat if different
					
			cur.execute('UPDATE rcs_data SET clanname = %s, clanLevel = %d, clanLeader = %s, members = %d, warFreq=(%s) WHERE clantag=(%s)', (clanName, clanLevel, clanLeader, members, warFreq, clanTag))
			
	except Exception:
		print("Error updating Database | DATA | ClanTag: {}".format(clantag))

def Clean_Database():
	try:
		cur.execute('SELECT clantag FROM public.coc_data')
		fetched = cur.fetchall()
		clantag = None

		for item in fetched:
			clantag = item[0]

			if '#' in clantag:
				fixedclantag = clantag.replace('#', '')

				cur.execute('UPDATE rcs_data SET clantag = %s WHERE clantag = %s', (fixedclantag, clantag))

	except Exception:
		print("Error Cleaning Database | DATA | ClanTag: {}".format(clantag))

# Main running of the code
if __name__ == '__main__':

	con = pymssql.connect(server=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD, database=DatabaseName, autocommit=True)
	cur = con.cursor()
	
	try:
		# Clean the DB and remove any X in the clantag
		try:
			Clean_Database()
		except:
			print('Failed to clean datebase')

		# Update Database from the API with new Clan Data
		try:
			UpdateDatabase()
		except Exception:
			print('Failed to update datebase')
			pass

		# Update the wiki page with the new data
		try:
			UpdateWikiPage(SUBREDDIT, WIKI_PAGE, PAGE_CONTENT)
		except Exception:
			print('Failed to update Wiki Page')
			pass

	except KeyboardInterrupt:
		print('Caught KeyboardInterrupt')
		sys.exit()
			
	except Exception:
		print('General Exception')

from datetime import datetime
import os, sys
import praw
import time
import requests
import psycopg2
import COC_oauth as oauth
import ctypes
import ConfigParser
import logging, logging.config

SUBREDDIT = 'RedditClanSystem'
APP_NAME = "Clash of Clans Clan Wiki Page Updater"
BotName = 'CoC Bot'
APP_VERS = '1.2.0'
LAST_REFRESH = 0 # Last time the oAth Refresh Key was grabbed
SleepTime = 10800 # = 3 hours
APIURL = 'https://set7z18fgf.execute-api.us-east-1.amazonaws.com/prod/?route=getClanDetails&clanTag=%23'
WIKI_PAGE = 'official_reddit_clan_system'
PAGE_CONTENT = ''


Config = ConfigParser.ConfigParser()
Config.read("/opt/skynet/Configs/config.ini")
DatabaseName = Config.get('Database', 'DatabaseName')
DB_USERNAME = Config.get('Database', 'Username')
DB_PASSWORD = Config.get('Database', 'Password')
DB_HOST = 'localhost'

# Setup logging
LoggerConfigLocation = '/opt/skynet/Configs/_Logger_Config.ini'
logging.config.fileConfig(LoggerConfigLocation, defaults={'BotName': BotName, 'APP_VERS': APP_VERS})
ExtraParameters = {'BotName': BotName, 'APP_VERS': APP_VERS}
logger = logging.LoggerAdapter(logging.getLogger(BotName+' v'+APP_VERS), extra=ExtraParameters)
	

def start():
	global r
	try:
		r = oauth.login()
		logger.info('//****** Started {} Version {} ******\\\\'.format(APP_NAME, APP_VERS), extra=ExtraParameters)
		return True
	except:
		logger.critical('Failed to Login')
		sys.exit()

def UpdateWikiPage(SUBREDDIT, WIKI_PAGE, PAGE_CONTENT):

	try:
		# Get existing wiki page data
		content = r.get_wiki_page(SUBREDDIT, WIKI_PAGE).content_md

		# Clans with No Requirements
		PAGE_CONTENT = ''
		start_marker = "[](#NRstart)"
		end_marker = "[](#NRend)"

		# Build the table
		cur.execute("SELECT * FROM public.coc_data WHERE classification='NR'")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Total&nbsp;members | Clan&nbsp;Tag | Leader&nbsp;Name | Requirements | Archer&nbsp;Level | War&nbsp;Frequency | Status | War&nbsp;Wins\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-|-'

		for item in fetched:
			# Set proper Status Text
			if str(item[7]) == 'inviteOnly':
				StatusText = 'Invite Only'
			elif str(item[7]) == 'closed':
				StatusText = 'Closed'

			# Set proper War Frequenct Text
			if str(item[6]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[6]) == 'always':
				WarFreqText = 'Always'
			elif str(item[6]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[6]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[6]) == 'never':
				WarFreqText = 'Never'

			# Set proper Requirements Text
			RequirementsText = ''
			if str(item[3]) == 'None':
				RequirementsText = ''
			else:
				RequirementsText = str(item[3])

			# Set proper Archer Level Text
			ArcherText = ''
			if str(item[4]) == 'None':
				ArcherText = ''
			else:
				ArcherText = str(item[4])

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[5]) + ') | ' + str(item[9]) + '/50 | [#' + str(item[1]) + '](https://clashofclans.com/clans/clan?clanTag=' + str(item[1]) + ') | /u/' + item[2] + ' | ' + RequirementsText + ' | ' + ArcherText + ' | ' + WarFreqText + ' | ' + StatusText + ' | ' + str(item[8])

		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))


		# Clans With Requirements

		PAGE_CONTENT = ''
		start_marker = "[](#WRstart)"
		end_marker = "[](#WRend)"

		# Build the table
		cur.execute("SELECT * FROM public.coc_data WHERE classification='WR'")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Total&nbsp;members | Clan&nbsp;Tag | Leader&nbsp;Name | Requirements | Archer&nbsp;Level | War&nbsp;Frequency | Status | War&nbsp;Wins\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-|-'

		for item in fetched:
			# Set proper Status Text
			if str(item[7]) == 'inviteOnly':
				StatusText = 'Invite Only'
			elif str(item[7]) == 'closed':
				StatusText = 'Closed'

			# Set proper War Frequenct Text
			if str(item[6]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[6]) == 'always':
				WarFreqText = 'Always'
			elif str(item[6]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[6]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[6]) == 'never':
				WarFreqText = 'Never'

			# Set proper Requirements Text
			RequirementsText = ''
			if str(item[3]) == 'None':
				RequirementsText = ''
			else:
				RequirementsText = str(item[3])

			# Set proper Archer Level Text
			ArcherText = ''
			if str(item[4]) == 'None':
				ArcherText = ''
			else:
				ArcherText = str(item[4])

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[5]) + ') | ' + str(item[9]) + '/50 | [#' + str(item[1]) + '](https://clashofclans.com/clans/clan?clanTag=' + str(item[1]) + ') | /u/' + item[2] + ' | ' + RequirementsText + ' | ' + ArcherText + ' | ' + WarFreqText + ' | ' + StatusText + ' | ' + str(item[8])


		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))

		logger.debug('Updated WR')

		# Competitive Clans

		PAGE_CONTENT = ''
		start_marker = "[](#CCstart)"
		end_marker = "[](#CCend)"

		# Build the table
		cur.execute("SELECT * FROM public.coc_data WHERE classification='CC'")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Total&nbsp;members | Clan&nbsp;Tag | Leader&nbsp;Name | Requirements | Archer&nbsp;Level | War&nbsp;Frequency | Status | War&nbsp;Wins\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-|-'

		for item in fetched:
			# Set proper Status Text
			if str(item[7]) == 'inviteOnly':
				StatusText = 'Invite Only'
			elif str(item[7]) == 'closed':
				StatusText = 'Closed'

			# Set proper War Frequenct Text
			if str(item[6]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[6]) == 'always':
				WarFreqText = 'Always'
			elif str(item[6]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[6]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[6]) == 'never':
				WarFreqText = 'Never'

			# Set proper Requirements Text
			RequirementsText = ''
			if str(item[3]) == 'None':
				RequirementsText = ''
			else:
				RequirementsText = str(item[3])

			# Set proper Archer Level Text
			ArcherText = ''
			if str(item[4]) == 'None':
				ArcherText = ''
			else:
				ArcherText = str(item[4])

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[5]) + ') | ' + str(item[9]) + '/50 | [#' + str(item[1]) + '](https://clashofclans.com/clans/clan?clanTag=' + str(item[1]) + ') | /u/' + item[2] + ' | ' + RequirementsText + ' | ' + ArcherText + ' | ' + WarFreqText + ' | ' + StatusText + ' | ' + str(item[8])

		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))

		logger.debug('Updated CC')

		# War Clans
		
		PAGE_CONTENT = ''
		start_marker = "[](#WCstart)"
		end_marker = "[](#WCend)"

		# Build the table
		cur.execute("SELECT * FROM public.coc_data WHERE classification='WC'")
		fetched = cur.fetchall()

		PAGE_CONTENT += 'Clan&nbsp;Name | Total&nbsp;members | Clan&nbsp;Tag | Leader&nbsp;Name | Requirements | Archer&nbsp;Level | War&nbsp;Frequency | Status | War&nbsp;Wins\n'
		PAGE_CONTENT += '-|-|-|-|-|-|-|-|-'

		for item in fetched:
			# Set proper Status Text
			if str(item[7]) == 'inviteOnly':
				StatusText = 'Invite Only'
			elif str(item[7]) == 'closed':
				StatusText = 'Closed'

			# Set proper War Frequenct Text
			if str(item[6]) == 'moreThanOncePerWeek':
				WarFreqText = '2+ / Week'
			elif str(item[6]) == 'always':
				WarFreqText = 'Always'
			elif str(item[6]) == 'oncePerWeek':
				WarFreqText = '1 / Week'
			elif str(item[6]) == 'unknown':
				WarFreqText = 'Unknown'
			elif str(item[6]) == 'never':
				WarFreqText = 'Never'

			# Set proper Requirements Text
			RequirementsText = ''
			if str(item[3]) == 'None':
				RequirementsText = ''
			else:
				RequirementsText = str(item[3])

			# Set proper Archer Level Text
			ArcherText = ''
			if str(item[4]) == 'None':
				ArcherText = ''
			else:
				ArcherText = str(item[4])

			PAGE_CONTENT += '\n[' + item[0].replace(' ', '&nbsp;') + '](/r/' + str(item[5]) + ') | ' + str(item[9]) + '/50 | [#' + str(item[1]) + '](https://clashofclans.com/clans/clan?clanTag=' + str(item[1]) + ') | /u/' + item[2] + ' | ' + RequirementsText + ' | ' + ArcherText + ' | ' + WarFreqText + ' | ' + StatusText + ' | ' + str(item[8])

		# Locate start and end markers
		start = content.index(start_marker)
		end = content.index(end_marker) + len(end_marker)
		content = content.replace(content[start:end], "{}{}{}".format(start_marker, PAGE_CONTENT, end_marker))

		logger.debug('Updated WC')

		try:
			r.edit_wiki_page(SUBREDDIT, WIKI_PAGE, content, reason="Updating Clan Tracking Wikipage")
			logger.info("Wiki page update for {} SUCCESS".format(SUBREDDIT), extra=ExtraParameters)
		except Exception:
			logger.exception("Wiki page update for {} FAILED".format(SUBREDDIT), exc_info=True, extra=ExtraParameters)


	except Exception:
		logger.exception("General Update Wiki Page Error", exc_info=True, extra=ExtraParameters)

def UpdateDatabase():
	try:
		cur.execute('SELECT clantag FROM public.coc_data')
		fetched = cur.fetchall()

		for item in fetched:
			clantag = item[0]

			clandata = requests.get(APIURL + clantag).json()

			clanname = clandata['clanDetails']['results']['name']
			typestatus = clandata['clanDetails']['results']['type']
			warfreq = clandata['clanDetails']['results']['warFrequency']
			warwins = clandata['clanDetails']['results']['warWins']
			members = clandata['clanDetails']['results']['members']

			cur.execute('UPDATE public.coc_data SET clanname=(%s), typestatus=(%s), warfreq=(%s), warwins=(%s), members=(%s) WHERE clantag=(%s)', (clanname, typestatus, warfreq, warwins, members, clantag))
			
			logger.debug("Updated {} - {} in the DB".format(clanname, clantag))
	except Exception:
		logger.exception("Error updating Database | DATA | ClanTag: {}".format(clantag), exc_info=True, extra=ExtraParameters)

def Clean_Database():
	try:
		cur.execute('SELECT clantag FROM public.coc_data')
		fetched = cur.fetchall()
		clantag = None

		for item in fetched:
			clantag = item[0]

			if '#' in clantag:
				fixedclantag = clantag.replace('#', '')

				cur.execute('UPDATE public.coc_data SET clantag=(%s) WHERE clantag=(%s)', (fixedclantag, clantag))
				
				logger.info("Cleaned {} in the DB".format(fixedclantag), extra=ExtraParameters)
	except Exception:
		logger.exception("Error Cleaning Database | DATA | ClanTag: {}".format(clantag), exc_info=True, extra=ExtraParameters)

# Main running of the code
if __name__ == '__main__':

	canStart = start()

	con = psycopg2.connect(host=DB_HOST, dbname=DatabaseName, user=DB_USERNAME, password=DB_PASSWORD)
	con.autocommit = True
	cur = con.cursor()
	logger.debug('Connected to Database')
	
	while canStart:

		try:

			# Clean the DB and remove any X in the clantag
			try:
				Clean_Database()
			except:
				logger.exception("Failed to Clean Datebase", exc_info=True, extra=ExtraParameters)

			# Update Database from the API with new Clan Data
			try:
				UpdateDatabase()
			except Exception:
				logger.exception("Failed to update Datebase", exc_info=True, extra=ExtraParameters)
				pass

			# Update the wiki page with the new data
			try:
				UpdateWikiPage(SUBREDDIT, WIKI_PAGE, PAGE_CONTENT)
			except Exception:
				logger.exception("Failed to update Wiki Page", exc_info=True, extra=ExtraParameters)
				pass

		except KeyboardInterrupt:
			logger.warning('Caught KeyboardInterrupt')
			sys.exit()
			
		except Exception:
			logger.critical('General Exception - sleeping 2 min', exc_info=True, extra=ExtraParameters)
			time.sleep(120)

		#logger.debug("Sleeping...")
		time.sleep(SleepTime)

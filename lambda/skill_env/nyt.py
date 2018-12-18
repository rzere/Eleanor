import json
import requests
import urllib2
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
import smtplib
import tweepy
import emoji

# We will create a class to be treated as an API for pulling data from the NYT API.
class APIController:

	def __init__(self):
		self.MOST_POPULAR_URL = 'https://api.nytimes.com/svc/mostpopular/v2/mostviewed/'
		self.TOP_STORIES_URL = 'http://api.nytimes.com/svc/topstories/v2/'
		self.COMMUNITY_URL = 'http://api.nytimes.com/svc/community/v3/user-content/url.json'
		self.API_KEY = '0c9485236fc3473f887afa4e6c50ae3d'
		self.params = {'api-key': self.API_KEY}
		self.news_api = NewsApiClient(api_key='3142bb731e6c4c9a99799f31b629985c')

		self.STATE_SET = {'LAUNCH','TOP_HEADLINES', 'TOPIC', 'CLOSE', 'CATEGORY'}
		self.CURRENT_STATE = 'LAUNCH'
		self.current_articles = {}
		self.currently_reading = None # The article we're looking at currently
		self.NYT_CATEGORIES = {'technology','business','sports','arts','automobiles','movies','food','style','education','books','opinion','travel','world','u.s.','science','health'}
		self.my_interests = {'arts', 'politics'}
		self.eleanor_emoji = emoji.emojize(":newspaper:" + ":statue_of_liberty:", use_aliases=True)

	def get_article_comments(self, url):
		p = self.params
		p['url'] = url

		http_response = requests.get(self.COMMUNITY_URL,params=p)
		comments = http_response.json()['results']['comments']
		if comments == []:
			return comments

		return_comments = []
		for comment in comments:
			comment_body = comment['commentBody'].replace("</br>", "").replace("<br/>","")
			if len(comment_body) <= 250: # Only return articles with length <= 100
				return_comments.append(comment)
				if len(return_comments) == 2:
					break

		return return_comments


	def get_personalized_articles(self):
		articles = []
		for category in list(self.my_interests):
			api_uri = self.MOST_POPULAR_URL + category + '/1.json'
			http_response = requests.get(api_uri,params=self.params)
			article = http_response.json()['results'][0]
			articles.append((article, category))
		self.current_articles['1'] = articles[0][0]
		self.current_articles['1']['description'] = self.current_articles['1']['abstract']
		self.current_articles['2'] = articles[1][0]
		self.current_articles['2']['description'] = self.current_articles['2']['abstract']
		#self.current_articles['3'] = articles[2][0]
		#self.current_articles['3']['description'] = self.current_articles['3']['abstract']
		return articles

	def get_articles_by_category(self, category):
		self.CURRENT_STATE = 'CATEGORY'
		#api_uri = self.MOST_POPULAR_URL + category + '/1.json'
		if category.lower() == "new york":
			category = "nyregion"
		api_uri = self.TOP_STORIES_URL + category + '.json'
		http_response = requests.get(api_uri,params=self.params)

		articles = http_response.json()['results'][:3]
		self.current_articles['1'] = articles[0]
		self.current_articles['1']['description'] = self.current_articles['1']['abstract']
		self.current_articles['2'] = articles[1]
		self.current_articles['2']['description'] = self.current_articles['2']['abstract']
		self.current_articles['3'] = articles[2]
		self.current_articles['3']['description'] = self.current_articles['3']['abstract']
		return articles


	def get_top_headlines(self):
		self.CURRENT_STATE = 'TOP_HEADLINES'
		response = self.news_api.get_top_headlines(sources='the-new-york-times')
		articles = response['articles'][:3] # Only take the first 3.....can modify later!
		self.current_articles['1'] = articles[0]
		self.current_articles['2'] = articles[1]
		self.current_articles['3'] = articles[2]
		return articles

	#def is_likely_not_headline(self, text):
	#	return text.startswith("By") or text.startswith("Advertisement") or text.startswith("Supported by")

	def get_articles_by_topic(self, topic):
		self.CURRENT_STATE = 'TOPIC'
		response = self.news_api.get_everything(q=topic, sources='the-new-york-times', sort_by='relevancy', from_param='2018-12-06')
		articles = response['articles']
		if articles == []:
			return articles

		#articles = articles[:3]
		NUM_ARTICLES = min(3, len(articles))
		for i in range(NUM_ARTICLES):
			self.current_articles[str(i+1)] = articles[i]
		#self.current_articles['1'] = articles[0]
		#self.current_articles['2'] = articles[1]
		#self.current_articles['3'] = articles[2]

		return_articles = []
		i, count = 0, 0
		while count < NUM_ARTICLES and i < len(articles):
			curr = articles[i]
			if ("New York Today" not in curr['title']) and ("California Today" not in curr['title']) and ("Briefing" not in curr['title']):
				return_articles.append(curr)
				count += 1
			i += 1
		return return_articles


	def get_article_by_url(self, url):
		http_response = urllib2.urlopen(url)
		article_soup = BeautifulSoup(http_response, 'html.parser')
		paragraphs = []
		for paragraph in article_soup.findAll('p'):
			paragraphs.append(paragraph.text)
		return " ".join(paragraphs)

	def send_to_email(self, article):
		gmail_user = "eleanor.cornell.tech@gmail.com"
		gmail_pwd = "Eleanorcornelltech"

		TO = "bz87@cornell.edu"
		SUBJECT = "Hey Ben, here's your article: " + article['title'].encode("ascii","ignore") + " - XOXO Eleanor"
		#TEXT = self.get_article_by_url(article['url']).encode("ascii","ignore")
		TEXT = "Here's a link to the article: \n"
		TEXT += article['url'] + '\n'
		TEXT += "Until next time! -- Eleanor" + self.eleanor_emoji

		server = smtplib.SMTP("smtp.gmail.com", 587)
		server.ehlo()
		server.starttls()
		server.login(gmail_user, gmail_pwd)
		BODY = '\r\n'.join(['To: %s' % TO,'From: %s' % gmail_user,'Subject: %s' % SUBJECT,'', TEXT])
		server.sendmail(gmail_user, [TO], BODY)

	def tweet_article(self,article):
		consumer_key ="y0Wgrtzyw2uPCGIiII1fr96q2"
		consumer_secret ="epvCM3omRVTgbjX9Jt7NsRAAJRqpqFqB9i1n5kiJ14ggAlAiGE"
		access_token ="1063255650401230848-oIYA2pCFstTBaK5VEQL6vB85IYUL87"
		access_token_secret ="xYPEztZYtVE1fnfVPRbv1Du7Gp2qOtrr9DidixiYRfwl7"

		auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
  
		# authentication of access token and secret 
		auth.set_access_token(access_token, access_token_secret) 
		api = tweepy.API(auth) 
  
		# update the status 
		api.update_status(status = article['url'] + '\n' + '#TweetsByEleanor ' + self.eleanor_emoji)


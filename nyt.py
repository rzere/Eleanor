import json
import requests
import urllib2
from bs4 import BeautifulSoup
#import newspaper
#import smtplib
#from email.mime.text import MIMEText

# We will create a class to be treated as an API for pulling data from the NYT API.
class APIController:

	def __init__(self):
		self.MOST_POPULAR_URL = 'https://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/1.json'
		self.TOP_STORIES_URL = 'http://api.nytimes.com/svc/topstories/v2/all-sections.json'
		self.ARTICLE_SEARCH_URL = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
		self.API_KEY = '0c9485236fc3473f887afa4e6c50ae3d'
		self.article_url_map = {}
		self.topic_url_map = {'politics': 'https://www.nytimes.com/section/politics'}
		self.params = {'api-key': self.API_KEY}
		#self.NYT_OBJ = newspaper.build('http://www.nytimes.com/')
		

	# Gets the top stories for a given time period (predefined to be 7 days), based on page view counts
	def get_top_articles(self):
		http_response = requests.get(url=self.MOST_POPULAR_URL,params=self.params)
		docs = http_response.json()['results']
		for d in docs:
			if d['title'] not in self.article_url_map:
				self.article_url_map[d['title']] = d['url']
		return docs

	# Gets the headlines of the top stories returned above
	def get_top_headlines(self):
		top_articles = self.get_top_articles()
		return [article['title'] for article in top_articles]

	# DOESN'T REALLY WORK UNFORTUNATELY!
	def get_articles_by_search(self, topic):
		p = self.params
		#p['q'] = topic
		p['fq'] = 'source:("The New York Times")' + ' AND ' + 'news_desk:("Sports" "Foreign")' 
		p['sort'] = 'newest'
		print(p)
		http_response = requests.get(url=self.ARTICLE_SEARCH_URL,params=p)
		docs = http_response.json()['response']['docs']
		return docs

	def is_likely_not_headline(self, text):
		return text.startswith("By") or text.startswith("Advertisement") or text.startswith("Supported by")

	def get_articles_by_topic(self, topic):
		topic_url = self.topic_url_map[topic]
		http_response = urllib2.urlopen(topic_url)
		article_soup = BeautifulSoup(http_response, 'html.parser')
		paragraphs = []
		for paragraph in article_soup.findAll('p'):
			if not self.is_likely_not_headline(paragraph.text.encode('ascii', 'ignore')):
				paragraphs.append(paragraph.text)
		return paragraphs


	def get_article_by_url(self, url):
		http_response = urllib2.urlopen(url)
		article_soup = BeautifulSoup(http_response, 'html.parser')
		paragraphs = []
		for paragraph in article_soup.findAll('p'):
			paragraphs.append(paragraph.text)
		return " ".join(paragraphs)


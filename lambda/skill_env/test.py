import nyt

controller = nyt.APIController()

def lambda_handler(event, context):
	if event["session"]["new"]:
		print('Starting new session!')
	if event["request"]["type"] == "LaunchRequest":
		return on_launch(event["request"], event["session"])
	elif event["request"]["type"] == "IntentRequest":
		return on_intent(event["request"], event["session"])
	elif event["request"]["type"] == "SessionEndedRequest":
		#return on_session_ended(event["request"], event["session"])
		#return on_session_ended()
		return handle_session_end_request()

# Useful functionality for handling different request types. There are 3 general
# request types:
#                1) LaunchRequest
#                2) IntentRequest
#                3) SessionEndedRequest

def on_launch(launch_request, session):
    return launch_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "HeadlinesIntent":
        return headlines_intent_response()
    elif intent_name == "TopicIntent":
    	return topic_intent_response(intent)
    elif intent_name == "ArticleIntent":
    	return article_intent_response(intent)
    elif intent_name == "CategoryIntent":
    	return category_intent_response(intent)
    elif intent_name == "FullArticleIntent":
    	return full_article_intent_response()
    elif intent_name == "PersonalizedArticlesIntent":
    	return personalized_articles_intent_response()
    elif intent_name == "CommentsIntent":
    	return comments_intent_response()
    elif intent_name == "InboxIntent":
    	return inbox_intent_response()
    elif intent_name == "CloseIntent":
    	return close_intent_response()
    elif intent_name == "TweetIntent":
    	return tweet_intent_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return on_session_ended("l", "r")
    else:
        raise ValueError("Invalid intent")

def on_session_ended(l,r):
    #session_attributes = {}
	#card_title = "CLOSE ELEANOR"
	#speech_output = "Bye Ben! Talk to you later"
	#reprompt_text = ""
	#should_end_session = True
	#return build_response(session_attributes, build_speechlet_response(
	#	card_title, speech_output, reprompt_text, should_end_session))
	print("Ending Session")
	
def launch_response():
	session_attributes = {}
	card_title = "LAUNCH ELEANOR"
	speech_output = "Hey, it's Eleanor! I'll be your conversational news assistant for The New York Times. What should we talk about?"
	reprompt_text = "Would you like to hear about the news Ben?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def close_intent_response():
	session_attributes = {}
	card_title = "CLOSE ELEANOR"
	speech_output = "Later Ben! Enjoy the cocktails after Open Studio!"
	reprompt_text = ""
	should_end_session = True
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def tweet_intent_response():
	article = controller.currently_reading
	controller.tweet_article(article)

	session_attributes = {}
	card_title = "TWEET"
	speech_output = "Done! Check your Twitter feed."
	reprompt_text = "Are you still there Ben?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))


def headlines_intent_response():
	#controller = nyt.APIController()
	articles = controller.get_top_headlines()
	article_titles = [a['title'] for a in articles]

	session_attributes = {}
	card_title = "TOP HEADLINES"

	speech_output = "Here are the top headlines: "
	for i in range(1,4):
		speech_output += "Article " + str(i) + ") " + article_titles[i-1] + ". "
	speech_output += "Would you like to hear one of these three articles?"

	reprompt_text = "Are you still there Ben?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def personalized_articles_intent_response():
	articles = controller.get_personalized_articles()
	article_titles = [a[0]['title'] for a in articles]

	session_attributes = {}
	card_title = "TOP HEADLINES"

	speech_output = "Here's some curated news just for you ben: "
	for i in range(1,3):
		speech_output += "In " + articles[i-1][1] + ": " + article_titles[i-1] + ". "
	speech_output += "Do any of these articles sound interesting to you?"

	reprompt_text = "Are you still there Ben?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def comments_intent_response():
	article_url = controller.currently_reading['url']
	comments = controller.get_article_comments(article_url)

	session_attributes = {}
	card_title = "COMMENTS RESPONSE"
	reprompt_text = "Are you still there Ben?"
	should_end_session = False

	if comments == []:
		speech_output = "Oh, it looks like noone has commented on this article yet."
		return build_response(session_attributes, build_speechlet_response(
			card_title, speech_output, reprompt_text, should_end_session))

	if len(comments) == 1:
		comment = comments[0]['commentBody'].replace("</br>", "").replace("<br/>","")
		#COMMENT_LENGTH = min(len(comment), 100)
		speaker = comments[0]['userDisplayName']
		speech_output = "Here's one perspective on this article: "
		speech_output += (speaker + ' says: ' + comment + "... ")
		return build_response(session_attributes, build_speechlet_response(
			card_title, speech_output, reprompt_text, should_end_session))

	speech_output = "Here are few perspectives on this article: "
	for c in comments:
		comment = c['commentBody'].replace("</br>", "").replace("<br/>","")
		#COMMENT_LENGTH = min(len(comment), 100)
		speaker = c['userDisplayName']
		speech_output += (speaker + ' says: ' + comment + ". ")

	return build_response(session_attributes, build_speechlet_response(
			card_title, speech_output, reprompt_text, should_end_session))
		



def category_intent_response(intent):
	## NOTE: DOES NOT HANDLE FAULTS. MAKE SURE THE CATEGORY IS SUPPORTED
	category = intent['slots']['CATEGORY']['value'].encode('ascii', 'ignore')
	articles = controller.get_articles_by_category(category)
	article_titles = [a['title'] for a in articles]

	session_attributes = {}
	card_title = "CATEGORY TITLES RESPONSE"

	speech_output = "Here's what's happening in " + category + ": "
	for i in range(1,4):
		speech_output += "Article " + str(i) + ") " + article_titles[i-1] + ". "
	speech_output += "Would you like to hear one of these three articles?"

	reprompt_text = "Are you still there Ben?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def topic_intent_response(intent):
	topic = intent['slots']['TOPIC']['value'].encode('ascii', 'ignore')

	articles = controller.get_articles_by_topic(topic)
	if articles == []:
		session_attributes = {}
		card_title = "TOPIC TITLES RESPONSE"
		speech_output= "Weird, I couldn't find any articles on that topic. Either try rephrasing the topic, or try a different topic."
		reprompt_text = "Are you still there Ben?"
		should_end_session = False
		return build_response(session_attributes, build_speechlet_response(
			card_title, speech_output, reprompt_text, should_end_session))

	N_ARTICLES = len(articles)
	article_titles = [a['title'] for a in articles]

	session_attributes = {}
	card_title = "TOPIC TITLES RESPONSE"

	if N_ARTICLES > 1:
		speech_output = "Here's some recent news that mentions " + topic + ": "
	else:
		speech_output = "Here's some recent news that mentions " + topic + ": "

	for i in range(1,N_ARTICLES+1):
		speech_output += "Article " + str(i) + ") " + article_titles[i-1] + ". "

	if N_ARTICLES > 1:
		speech_output += "Would you like to hear one of these articles?"
	else:
		speech_output += "Would you like to hear this article?"

	reprompt_text = "Are you still there Ben?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def article_intent_response(intent):
	article_number = intent['slots']['ARTICLE_NUMBER']['value'].encode('ascii', 'ignore')
	article = controller.current_articles[article_number]
	controller.currently_reading = article ## Keep track of what article we're reading!

	session_attributes = {}
	card_title = "ARTICLE DESCRIPTION RESPONSE"

	speech_output = "Here's a bit about article " + article_number + ": " + article['description'] + ". "
	speech_output += "Would you like to hear the full article? I could also send the article to your inbox or tweet it."

	reprompt_text = "Are you still there Ben?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def full_article_intent_response():
	article_url = controller.currently_reading['url']
	return get_article_by_url(article_url)

def inbox_intent_response():
	article = controller.currently_reading
	controller.send_to_email(article)

	session_attributes = {}
	card_title = "INBOX"
	speech_output = "Check your inbox! The article should be there."
	reprompt_text = "This is awkward. Are you still there?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

	

def get_article_by_url(url):
	article = controller.get_article_by_url(url)
	# TODO: Check to make sure that the article isn't too long for an Alexa response.
	#       If it is, only return a chunk of the article....
	#		Let's say the first 5000 characters for now
	RETURN_LENGTH = min(5000,len(article))
	session_attributes = {}
	card_title = "FULL ARTICLE FROM URL"
	speech_output = "Here's the full article: "
	speech_output += article[:RETURN_LENGTH] + ". "
	reprompt_text = "Would you like to continue?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))


# Useful functionality for constructing json responses to be sent back to the user.

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }
	
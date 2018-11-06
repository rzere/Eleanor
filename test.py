import nyt

def lambda_handler(event, context):
	if event["session"]["new"]:
		print('Starting new session!')
	if event["request"]["type"] == "LaunchRequest":
		on_launch(event["request"], event["session"])
	elif event["request"]["type"] == "IntentRequest":
		return on_intent(event["request"], event["session"])
	elif event["request"]["type"] == "SessionEndedRequest":
		return on_session_ended(event["request"], event["session"])


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
    elif intent_name == "ArticlesIntent":
    	return articles_intent_response()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print("Ending session.")

def launch_response():
	session_attributes = {}
	card_title = "LAUNCH ELEANOR"
	speech_output = "Welcome to Eleanor! I'll be your conversational news assistant for The New York Times."
	reprompt_text = "Would you like to hear about the news?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))


def headlines_intent_response():
	controller = nyt.APIController()
	headlines = controller.get_top_headlines()

	session_attributes = {}
	card_title = "TOP HEADLINES"
	speech_output = "Here are the top headlines: " + ", ".join(headlines)
	reprompt_text = "Would you like more information?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def articles_intent_response():
	controller = nyt.APIController()
	articles = controller.get_top_articles()

	title_to_url = {a['title']:a['url'] for a in articles}

	session_attributes = {}
	card_title = "TOP ARTICLES"
	speech_output = "Here are the top articles: " + str(articles)
	reprompt_text = "Would you like more information?"
	should_end_session = False
	return build_response(session_attributes, build_speechlet_response(
		card_title, speech_output, reprompt_text, should_end_session))

def get_article_by_url(url):
	controller = nyt.APIController()
	article = controller.get_article_by_url(url)
	session_attributes = {}
	card_title = "FULL ARTICLE FROM URL"
	speech_output = article
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
	
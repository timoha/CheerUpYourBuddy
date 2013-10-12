from bottle import route, run, template
import urllib.parse
import urllib.request
import subprocess
import json
from string import ascii_letters

from data import word_sentiments
from ucb import main, trace, interact, log_current_line

app_id = "221563731244990"
app_secret = "544e64364be4a1e1a5d6ffa695d9425a"
post_login_url = "http://0.0.0.0:8080/"
oauth_access_token = "CAACEdEose0cBAHS2efWZCr5ivAlBnSlpud6RTcDOYmQJWMxiIFWhK08tmfdns4FW7moW4XRSmArPdZA9o0ZC0VJZCiZAWyRmxZANY7CvoqrXP70ZAsqyCETL80jbZBL766wyXw7nFdildfjsCHc5ZBpWoWbkpfzf414tTdi5aGyi6sq3ofrKonvqctjDBVxd3ZC5oZD"


def get_all_statuses_by_friend(friends):
    statuses_by_friends = {}
    for friend in friends:
        uid = get_friend_id(friend)
        statuses_by_friends[uid] = get_friend_messages(uid)
    return statuses_by_friends


def get_friend_id(friend):
    return friend['uid']


def get_friend_messages(uid):
    query = "SELECT message FROM status WHERE uid = " + str(uid)
    return get_data(get_query(query))


def get_friends():
    query = "SELECT uid,name, pic_square FROM user WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me())"
    return get_data(get_query(query))


def get_friends_posts():
    query = "SELECT message, uid FROM status WHERE uid IN (SELECT uid1 FROM friend WHERE uid2=me())"
    return get_data(get_query(query))


def status_message(status):
    return status['message']


def status_friend_id(status):
    return status['uid']


def status_words(status):
    """Return the words in a tweet."""
    return extract_words(status)


def extract_words(text):
    """Return the words in a tweet, not including punctuation."""
    clean_text = ''
    for char in text:
        if char in ascii_letters:
            clean_text += char
        else:
            clean_text += ' '
    return clean_text.split()


def make_sentiment(value):
    """Return a sentiment, which represents a value that may not exist.
    """
    assert value is None or (value >= -1 and value <= 1), 'Illegal value'
    return value


def has_sentiment(s):
    """Return whether sentiment s has a value."""
    return s is not None


def sentiment_value(s):
    """Return the value of a sentiment s."""
    assert has_sentiment(s), 'No sentiment value'
    return s


def analyze_status_sentiment(status):
    average = make_sentiment(None)
    total, count = 0, 0
    words = status_words(status_message(status))
    for word in words:
        word_sentiment = get_word_sentiment(word)
        if has_sentiment(word_sentiment):
            total += sentiment_value(word_sentiment)
            count += 1
    if count > 0:
        average = make_sentiment(total / count)
    return average


def get_word_sentiment(word):
    """Return a sentiment representing the degree of positive or negative
    feeling in the given word.
    """
    # Learn more: http://docs.python.org/3/library/stdtypes.html#dict.get
    return make_sentiment(word_sentiments.get(word))


def get_query(query):
    return urllib.parse.urlencode({'q': query, 'access_token': oauth_access_token})


def get_data(query):
    url = "https://graph.facebook.com/fql?" + query
    data = json.loads(urllib.request.urlopen(url).read().decode("utf-8"))
    return data["data"]


def group_statuses_by_friends(statuses):
    statuses_by_friends = {}
    for status in statuses:
        friend_id = status['uid']
        if friend_id in statuses_by_friends:
            statuses_by_friends[friend_id].append(status_message(status))
        else:
            statuses_by_friends[friend_id] = [status_message(status)]
    return statuses_by_friends


def average_sentiments(statuses_by_friends):
    averaged_friend_sentiments = {}
    for friend in statuses_by_friends:
        total, count = 0, 0
        for status in statuses_by_friends[friend]:
            status_sentiment = analyze_status_sentiment(status)
            if has_sentiment(status_sentiment):
                total += sentiment_value(status_sentiment)
                count += 1
        if count > 0:
            averaged_friend_sentiments[friend] = sentiment_value(
                make_sentiment(total / count))
    return averaged_friend_sentiments


def get_friend_by_id(uid, friends):
    for friend in friends:
        if get_friend_id(friend) == uid:
            return friend

# app = Flask(__name__)


@route('/')
def get_average_sentiments():
    return_friends = []
    friends = get_friends()
    sentiments = average_sentiments(get_all_statuses_by_friend(friends))
    sentiments = sorted(sentiments.items(), key=lambda x: x[1])
    for sentiment in sentiments:
        friend = get_friend_by_id(sentiment[0], friends)
        friend['sentiment'] = sentiment[1]
        return_friends.append(friend)
    return template('index', friends=return_friends)

run(host='localhost', port=5000)



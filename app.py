import os
import requests
import parser
from bs4 import BeautifulSoup

from firebase import firebase

from flask import Flask, jsonify, json, request

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

grammar_base = "https://languagetool.org/api/v2/check"
fire = firebase.FirebaseApplication('https://newscheck-e0069.firebaseio.com', None)


# Test Route
@app.route('/hello', methods=['GET'])
def index():
    return "hello!"


# Check Route Checks the Url, Retrieves News and Sends Ratings as Response
@app.route('/check', methods=['POST'])
def check():

    url = request.json['url']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    site = requests.get(url, headers=headers)
    newssite = site.text
    url = site.url
    url = url.replace('http://', '')
    url = url.replace('https://', '')
    url = url.replace('www.', '')
    url = str.split(url, '/')[0]

    rating = getRatings(url)
    soup = BeautifulSoup(newssite, "html.parser")
    for elem in soup.findAll(['script', 'style', 'iframe', 'nav', 'img']):
        elem.extract()

    textarr = soup.get_text().split('\n')
    text = ""
    textarr = [x.strip() for x in textarr if x.strip() is not "" and len(x.strip()) > 50]
    for x in textarr:
        text = text + x + " "


    grammar = requests.post(grammar_base, {'text': text, 'language': 'auto'}).json()
    score = (2.5 - len(grammar['matches'])/len(text)*75) + rating['rating']*0.75

    key, userRating = getUserRatings(url)
    if userRating is not None:
        if userRating['reviews'] < 50:
            score = (score*(100-userRating['reviews'])/100) + (userRating['score']*userRating['reviews']/100)
        else:
            score = (score/2) + (userRating['score']/2)

    score = score + not_recommended(url)

    if score >= 7:
        status = "This news and source is trustworthy"
    elif score >= 4:
        status = "No red flags detected, Proceed with caution"
    else:
        status = "This source and news is most likely fake"

    score = score*10

    return jsonify(data={'score': score, 'suggestion': status})


#From Parser.py
def not_recommended(url):
    # Assigns a not_recommended score to a url
    # Check for known urls
    if 'com.co' in url:
        return -2

    return 0

def getRatings(url):

    result = fire.get('/sources', None)

    for k, v in result.items():
        if url in v['url']:
            return v

    return {"rating": 5, "notfound": True, "confidence": False}

def getUserRatings(url):

    result = fire.get('/userfeedback', None)

    for k, v in result.items():
        if url in v['url']:
            return k, v

    return len(result.items()), None


@app.route('/user/feedback', methods=['PUT'])
def registerFeedback():

    url = request.json['url']
    feedback = request.json['feedback']
    fireUrl = '/userfeedback'

    url = url.replace('http://', '')
    url = url.replace('https://', '')
    url = url.replace('www.', '')
    url = str.split(url, '/')[0]

    key, rating = getUserRatings(url)

    if(rating is not None):
        n = rating['reviews']
        rating['reviews'] = n + 1
        score = rating['score']*n
        score += feedback
        rating['score'] = score/(n+1)
        fireUrl = fireUrl + "/" + key
        fire.patch(fireUrl, rating)
    else:
        rating = {'reviews': 1, 'score': feedback, 'url': url}
        fire.post(fireUrl, rating)

    return jsonify(data=rating)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

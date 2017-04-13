import os
import requests
from bs4 import BeautifulSoup

from flask import Flask, request, jsonify, json, request

app = Flask(__name__)
grammar_base = "https://languagetool.org/api/v2/check"

@app.route('/hello', methods=['GET'])
def index():
  return "hello!"

@app.route('/check', methods=['POST'])
def check():

  url = request.json['url'];

  newssite = requests.get(url).text;
  soup = BeautifulSoup(newssite, "html.parser")
  for elem in soup.findAll(['script', 'style', 'iframe', 'nav', 'img']):
    elem.extract()

  grammar = requests.post(grammar_base, {'text': soup.get_text(), 'language': 'auto'}).json()
  textarr = soup.get_text().split('\n')
  textarr = [x.strip() for x in textarr if x.strip() is not "" and len(x.strip()) > 75]
  return jsonify(x={"uri": textarr})

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port, debug=True)

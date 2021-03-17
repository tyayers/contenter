import web
from textblob import TextBlob
import feedparser
import json
import random
import string
import requests
import time
import datetime
from datetime import date
from google.oauth2 import service_account
from google.cloud import bigquery

urls = (
    '/news(.*)', 'news',
    '/github(.*)', 'github'
)
app = web.application(urls, globals())

class news:
  def Search(self, topic):
    d = feedparser.parse('https://news.google.com/rss/search?q=' + topic + '?hl=en-US&gl=US&ceid=US:en')
    count = 0
    polarity = 0
    subjectivity = 0

    for x in d.entries:
      count += 1
      parts = TextBlob(x.title)
      polarity += parts.sentiment.polarity
      subjectivity += parts.sentiment.subjectivity
    
    polarity = polarity / count
    subjectivity = subjectivity / count
    return (count, polarity, subjectivity)

  def GET(self, name):
    articles = []

    d = feedparser.parse('https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en')
    for x in d.entries:
      parts = TextBlob(x.title)
      item = {
        "id": ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8)),
        "title": x.title,
        "link": x.link,
        "published": x.published,
        "source": x.source.title,
        "sourcelink": x.source.href,
        "topics": parts.noun_phrases
      }

      # Remove last topic (is usually the name of the source)
      item["topics"].pop(len(item["topics"]) - 1)

      articles.append(item)

    #print(json.dumps(articles, indent=2))
    return articles

class github:
  def GET(self, name):
    web.header('Content-Type', 'application/json')
    companies = [
      {
        "name": "microsoft",
        "github": ["microsoft", "azure"],
        "reddit": "azure",
        "stock_symbol": "MSFT"
      },
      {
        "name": "google",
        "github": ["google", "kubernetes", "googlecloudplatform"],
        "reddit": "googlecloud",
        "stock_symbol": "GOOG"
      }, 
      {
        "name": "deutschebank",
        "reddit": "",
        "stock_symbol": "DB"
      },
      {
        "name": "adobe", 
        "reddit": "adobe",
        "stock_symbol": "ADBE"
      },
      {
        "name": "salesforce",
        "reddit": "salesforce",
        "stock_symbol": "CRM"
      },
      {
        "name": "aws",
        "reddit": "aws",
        "stock_symbol": "AMZN"
      },
      {
        "name": "facebook",
        "reddit": "facebook",
        "stock_symbol": "FB"
      },
      {
        "name": "ibm",
        "github": ["ibm", "RedHatOfficial"],
        "reddit": "ibm",
        "stock_symbol": "IBM"
      },
      {
        "name": "twitter",
        "reddit": "twitter",
        "stock_symbol": "TWTR"
      },
      {
        "name": "siemens",
        "stock_symbol": "SIE"
      }
    ]
    results = []

    newsservice = news()

    for x in companies:
      if not "github" in x:
        x["github"] = [x["name"]]
      
      if not "reddit" in x:
        x["reddit"] = x["name"]

      data = {
        "company": x["name"],
        "date": str(date.today()),
        "github_stars": 0,
        "github_forks": 0,
        "reddit_subscribers": 0,
        "news_stories": 0,
        "news_polarity": 0,
        "news_subjectivity": 0,
        "stock_price": 0
      }

      for githubuser in x["github"]:
        r = requests.get(url='https://api.github.com/search/repositories?q=user:' + githubuser + "&sort=stars&per_page=100")
        if "items" in r.json():
          for item in r.json()["items"]:
            data["github_stars"] += item["stargazers_count"]
            data["github_forks"] += item["forks"]
        else:
          print(r.json())

      if x["reddit"] != "":
        rurl = "https://www.reddit.com/r/" + x["reddit"] + "/about.json"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url=rurl, headers=headers)
        if "data" in r.json():
          data["reddit_subscribers"] = r.json()["data"]["subscribers"]

      newsdata = newsservice.Search(x["name"])
      data["news_stories"] = newsdata[0]
      data["news_polarity"] = round(newsdata[1], 6)
      data["news_subjectivity"] = round(newsdata[2], 6)

      if x["stock_symbol"] != "":
        r = requests.get(url='https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=' + x["stock_symbol"] + '&apikey=FNT06P1FPP3XUTCW')
        if "Time Series (Daily)" in r.json():
          key = list(r.json()["Time Series (Daily)"].keys())[0]
          data["stock_price"] = float(r.json()["Time Series (Daily)"][key]["4. close"])
        else:
          print(r.json())

      results.append(data)
      time.sleep(21)

    self.saveToBigQuery(results)
    return json.dumps(results)

  def saveToBigQuery(self, data):
    credentials = service_account.Credentials.from_service_account_file('./svc-account.json')
    client = bigquery.Client(credentials=credentials)

    errors = client.insert_rows_json("bruno-1407a.contenter.companies", data)
    if errors == []:
        print("New rows have been added.")
    else:
        print("Encountered errors while inserting rows: {}".format(errors))

  # def get_new_token():

  #   auth_server_url = "https://dm-us.informaticacloud.com/authz-service/oauth/token"
  #   client_id = 'Jl88QzqE3GYvaibOVb1Fx'
  #   client_secret = '9xy23jdl'

  #   token_req_payload = {'grant_type': 'client_credentials'}

  #   token_response = requests.post(auth_server_url,
  #   data=token_req_payload, verify=False, allow_redirects=False,
  #   auth=(client_id, client_secret))
          
    # if token_response.status_code !=200:
    #   print("Failed to obtain token from the OAuth 2.0 server", file=sys.stderr)
    #   sys.exit(1)

    #   print("Successfuly obtained a new token")
    #   tokens = json.loads(token_response.text)
    #   return tokens['access_token']


if __name__ == "__main__":
    app.run()

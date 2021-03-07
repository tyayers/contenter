import web
from textblob import TextBlob
import feedparser
import json
import random
import string
import requests
import time

urls = (
    '/news(.*)', 'news',
    '/github(.*)', 'github'
)
app = web.application(urls, globals())

class news:
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
        "reddit": "azure"
      },
      {
        "name": "google",
        "github": ["google", "kubernetes", "googlecloudplatform"],
        "reddit": "googlecloud"
      }, 
      {
        "name": "deutschebank",
        "reddit": ""
      },
      {
        "name": "adobe", 
        "reddit": "adobe",
      },
      {
        "name": "salesforce",
        "reddit": "salesforce"
      },
      {
        "name": "aws",
        "reddit": "aws"
      }
    ]
    results = []

    for x in companies:
      if not "github" in x:
        x["github"] = [x["name"]]

      data = {
        "company": x["name"],
        "github_stars": 0,
        "github_forks": 0,
        "reddit_subscribers": 0
      }

      for githubuser in x["github"]:
        r = requests.get(url='https://api.github.com/search/repositories?q=user:' + githubuser + "&sort=stars&per_page=100")
        if "items" in r.json():
          for item in r.json()["items"]:
            data["github_stars"] += item["stargazers_count"]
            data["github_forks"] += item["forks"]

      if x["reddit"] != "":
        rurl = "https://www.reddit.com/r/" + x["reddit"] + "/about.json"
        headers = {'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"', 'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url=rurl, headers=headers)
        if "data" in r.json():
          data["reddit_subscribers"] = r.json()["data"]["subscribers"]

      results.append(data)
      #time.sleep(1)

    return json.dumps(results)

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

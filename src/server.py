import web
from textblob import TextBlob
import feedparser
import json
import random
import string

urls = (
    '/(.*)', 'news'
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

if __name__ == "__main__":
    app.run()

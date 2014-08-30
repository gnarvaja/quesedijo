import sys
import feedparser
import datetime
import pprint
import simplejson
import flask
import calendar
import yaml
from collections import namedtuple

app = flask.Flask(__name__)

Period = namedtuple("Period", "from_ to_ words")
Word = namedtuple("Word", "word freq")

field_weights = {
    "summary": 2,
    "description": 1,
    "tags": 3,
}

common_words = "muy,de,la,el,y,del,en,los,las,a,para,un,una,con,que,al,su,por,mi,es,como".split(",")


def tokenizer(value):
    words = split_words(value)
    count = {}
    for w in words:
        if w in count:
            count[w] += 1
        else:
            count[w] = 1
    return count.items()


def split_words(value):
    value = value.lower()
    ret = []
    for word in value.split(","):
        ret.extend([w for w in word.split(" ") if w and w not in common_words])
    return ret


class FeedSource:
    def __init__(self, feedURL):
        self.feedURL = feedURL
        self.feed = feedparser.parse(self.feedURL)

    class DocumentAdapter:
        def __init__(self, item):
            self.item = item

        def get_date(self):
            date = datetime.date(*self.item.published_parsed[:3])
            return date

        def get_fields(self):
            ret = {"summary": self.item.summary}
            if self.item.summary != self.item.description:
                ret["description"] = self.item.description
            return ret.items()

    def get_documents(self):
        feed = self.feed
        for item in feed["entries"]:
            yield self.DocumentAdapter(item)


def get_period(doc, period_type):
    d = doc.get_date()
    if period_type == "day":
        return d, d
    elif period_type == "month":
        _, day_to = calendar.monthrange(d.year, d.month)
        return datetime.date(d.year, d.month, 1), datetime.date(d.year, d.month, day_to)
    elif period_type == "week":
        week_day = d.weekday()
        return d - datetime.timedelta(days=week_day), d + datetime.timedelta(days=6-week_day)


def calculate_source_cloud(source, period_type="day"):
    source_tag_cloud = {}

    for doc in source.get_documents():
        from_, to_ = get_period(doc, period_type)
        if not (from_, to_) in source_tag_cloud:
            source_tag_cloud[(from_, to_)] = {}
        tag_cloud = source_tag_cloud[(from_, to_)]

        for field, value in doc.get_fields():
            tokens = tokenizer(value)
            for token, count in tokens:
                tag_cloud[token] = tag_cloud.get(token, 0) + field_weights[field] * count

    sorted_periods = sorted(source_tag_cloud.items(), key=lambda x: x[0][0])
    ret = []
    for (from_, to_), tag_cloud in sorted_periods:
        sorted_words = sorted(tag_cloud.items(), key=lambda (word, freq): -freq)
        words = [Word(word, freq) for word, freq in sorted_words]
        if words:
            ret.append({
                "from": from_.strftime("%Y-%m-%d"),
                "to": to_.strftime("%Y-%m-%d"),
                "words": words
                })
    return ret


parsed_sources = {}


@app.route("/")
def index():
    template = """<html>
        <body>
            <form action="/add_source" method="GET">
                Nombre: <input type="text" name="name"> <br/>
                URL: <input type="text" name="url">
                <input type="submit">
            </form>
            Fuentes actuales:
            <dl>
                %s
            </dl>
            <ul>
                <li><a href="/day">Por dia</a></li>
                <li><a href="/week">Por semana</a></li>
                <li><a href="/month">Por mes</a></li>
            </ul>
        </body>
        </html>
        """
    content = ""
    for name, source in parsed_sources.items():
        content += "<dt>%s</dt> <dd>%s</dd>\n" % (name, source.feedURL)
    return template % content

@app.route("/add_source")
def add_source():
    source_url = flask.request.args.get("url")
    source_name = flask.request.args.get("name")
    if source_url not in parsed_sources:
        parsed_sources[source_name] = FeedSource(source_url)
        return "OK"
    else:
        return "Ya estaba"

@app.route("/<period_type>")
def show(period_type="day"):
    ret = []
    for source_name, source in parsed_sources.items():
        ret.append({
            "name": source_name,
            "periodos": calculate_source_cloud(source, period_type)
        })
    return simplejson.dumps({"medios": ret})

if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0")

if __name__ == "__main__":
    result = calculate_source_cloud(FeedSource(sys.argv[1]))
    print yaml.dump(result)


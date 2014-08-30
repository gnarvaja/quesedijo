#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import feedparser
import datetime
import simplejson
from flask import make_response, request, current_app
from functools import update_wrapper
import flask
import calendar
from collections import namedtuple

app = flask.Flask(__name__)
application = app

Period = namedtuple("Period", "from_ to_ words")
Word = namedtuple("Word", "word freq")

field_weights = {
    "summary": 2,
    "description": 1,
    "tags": 3,
}

common_words = "todo,am,muy,de,la,el,y,del,en,los,las,a,para,un,una,unos,con,que,al,su,por,mi,es,como".split(",")
preposiciones="a,ante,bajo,cabe,con,contra,de,desde,durante,en,entre,hacia,hasta,mediante,para,por,según,sin,so,sobre,tras,versus,vía".split(",")
otras="no,como,qué,cuándo,cuánto,cuando,que,por,entrevista,mañana".split(",")
common_words.extend(preposiciones)
common_words.extend(otras)


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, datetime.timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

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
    ret = filter(lambda w: w and not w.isdigit(), ret)
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
        sorted_words = sorted(tag_cloud.items(), key=lambda (word, freq): freq, reverse=True)
        words = [Word(word, freq) for word, freq in sorted_words]
        if words:
            ret.append({
                "from": from_.strftime("%Y-%m-%d"),
                "to": to_.strftime("%Y-%m-%d"),
                "words": words[:40]
                })
    return ret


parsed_sources = {}


@app.route("/")
@crossdomain(origin="*")
def index():
    template = """<html>
        <body>
            <form action="add_source" method="GET">
                Nombre: <input type="text" name="name"> <br/>
                URL: <input type="text" name="url">
                <input type="submit">
            </form>
            Fuentes actuales:
            <dl>
                %s
            </dl>
            <ul>
                <li><a href="day">Por dia</a></li>
                <li><a href="week">Por semana</a></li>
                <li><a href="month">Por mes</a></li>
            </ul>
        </body>
        </html>
        """
    content = ""
    for name, source in parsed_sources.items():
        content += "<dt>%s</dt> <dd>%s</dd>\n" % (name, source.feedURL)
    return template % content

@app.route("/add_source")
@crossdomain(origin="*")
def add_source():
    source_url = flask.request.args.get("url")
    source_name = flask.request.args.get("name")
    if source_url not in parsed_sources:
        parsed_sources[source_name] = FeedSource(source_url)
        return "OK"
    else:
        return "Ya estaba"

@app.route("/<period_type>")
@crossdomain(origin="*")
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


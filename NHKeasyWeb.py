# -*- coding: utf-8 -*-

import json
from urllib.request import urlopen, Request
import re


BASE_URL = "https://www3.nhk.or.jp/news/easy/"
HTML_OUT_PATH = '/home/pi/NHKeasy/html/'


def json_get():
    url = BASE_URL + 'news-list.json'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(req)
    wjson = data.read().decode('utf-8-sig')
    wjdata = json.loads(wjson)
    return wjdata


def json_parse(data):
    date = get_date()
    return_data = []
    for i, article in enumerate(data[0][date]):
        return_data.append(i)
        return_data[i] = {
            'title': article['title'],
            'date': article['news_publication_time'],
            'id': article['news_id']
        }
    return return_data

def html_parse(articleid):
    htmlurl = BASE_URL + articleid + '/' + articleid + '.html'
    req = Request(htmlurl, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    html = webpage.decode('utf-8')
    title = html.split('<h1 class="article-main__title">')[1].split('</h1>')
    title_text = re.sub(r'\s*\n\s*', '', title[0])
    article = html.split('id="js-article-body">')[1].split('</div>')[0]
    article_text = re.sub(r'<(?!(/?(ruby\s?)|/?(rt\s?))).*?>', '', article)
    article_text = re.sub(r'^\n\s+', '', re.sub(r'\n*\s+$', '', article_text))
    return [title_text, article_text]


def format_date(date):
    parts = date.split("-")
    day_and_time = parts[2].split(" ")
    return parts[0] + "年" + parts[1] + "月" + day_and_time[0] + "日"


def build_xhtml():
    data = json_parse(json_get())
    xhtml = '''
        <!DOCTYPE html>
        <html lang="ja">
            <head>
                <meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />
                <style type="text/css">
                    @charset "utf-8";
                    body {
                        writing-mode: tb-rl;
                        -epub-writing-mode: vertical-rl;
                        -webkit-writing-mode: vertical-rl;
                        line-break: normal;
                        -epub-line-break: normal;
                        -webkit-line-break: normal;
                        text-orientation: upright;
                        -epub-text-orientation: upright;
                        -webkit-text-orientation: upright;
                        padding-bottom: 30px;
                        overflow-y: hidden;
                    }
                    h1 {
                        font-size: 1.2em
                    }
                </style>
        </head>
        <body>
            <div id="top"></div>
    '''
    for i, content in enumerate(data):
        t_t = html_parse(content['id'])
        xhtml += '<h1>' + t_t[0] + '</h1><br>'
        xhtml += format_date(content['date']) + '<br><br>'
        xhtml += t_t[1] + '<br><br><br>'
    xhtml += '</body></html>'
    return xhtml.encode('utf-8')


def make_file(xhtml):
    date = get_date()
    file = open(HTML_OUT_PATH + date + ".html", "wb")
    file.write(xhtml)
    file.close()


def get_date():
    data = json_get()
    keys = list(data[0].keys())
    keys.sort(reverse=True)
    return keys[0]


if __name__ == '__main__':
    print('Creating source files...')
    make_file(build_xhtml())
    print("Success: HTML File created")


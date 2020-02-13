
from flask import Flask, redirect, url_for, request, render_template
from search_api import *
from url_Crawler import start_crawl
from flask_table import Table, Col
from url_crawler_async_pipe2 import start_crawl as start_async_crawl
from wrk_benchmark_test import run_test
import os



# Declare your table
class ItemTable(Table):
    title = Col('Title')
    description = Col('Description')
    url = Col('Url')
    image = Col('image')

# Get some objects
class Item(object):
    def __init__(self, title, description, url, image):
        self.title = title
        self.description = description
        self.url = url
        self.image = image


app = Flask(__name__)

@app.route('/sync/<keyword>')
def crawl_by_sync(keyword):
    sub_links = ItemTable(start_crawl(keyword), border=1, no_items='내용없음')
    return render_template('result2.html', table=sub_links)

@app.route('/async/<keyword>')
def crawl_by_async(keyword):
    sub_links = ItemTable(start_async_crawl(keyword), border=1, no_items='내용없음')
    return render_template('result2.html', table=sub_links)

@app.route('/benchmark/<keyword>')
def start_benchmark_test(keyword):
    run_test()
    return render_template('image.html',async_image = 'async_image.png', sync_image = 'sync_image.png' )

@app.route('/search', methods = ['POST', 'GET'])
def get_keyword():
   if request.method == 'POST':
      action = None
      keyword = request.form['keyWord'] 
      print(request.form['keyWord'] )
      if request.form['action'] == 'Sync':
        action = 'crawl_by_sync'
      elif request.form['action'] == 'Async':
        action = 'crawl_by_async'
      elif request.form['action'] == 'Benchmark_test':
        action = 'start_benchmark_test'
        keyword = 'test'
      return redirect(url_for(action, keyword = keyword))


@app.route("/")
def main():
    return render_template('index2.html')
if __name__ == '__main__':
    app.run(debug = True)
    #app.run()



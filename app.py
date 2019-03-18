from flask import Flask, render_template, json, request, redirect, url_for, make_response
from elasticsearch import Elasticsearch

from controller import es_pull_scroll


app = Flask(__name__)


@app.route('/')
def application_start():
    """
    Default Route, Rendering `index.html`

    :return:    `index.html`
    """
    return render_template("index.html", object_list=[])


@app.route('/search/<keyword>', methods=['GET'])
def search_keyword(keyword):
    """
    GET `keyword`, fuzzy match keyword in Elasticsearch using scroll api
    Renders `index.html` with Elasticsearch results using Jinja2

    :param keyword:
    :return:        `index.html`
    """
    output_dictionary_list = es_pull_scroll.es_search(keyword)
    return render_template("index.html", object_list=output_dictionary_list)


if __name__ == "__main__":
    app.run(port=5002, debug=True, use_reloader=True)

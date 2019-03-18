from elasticsearch import Elasticsearch
from elasticsearch import helpers as es_helpers
import traceback
import json
import sys

from config import es_host, es_port, es_index, es_doc_type


# Elasticsearch Client
es_client = Elasticsearch([es_host], port=es_port)


def es_search(keyword):
    """
    Fuzzy search Elasticsearch for the provided `keyword`
    Uses Elasticsearch Scroll API to get all the matching documents
    `preserve_order` is set to True, Documents are sorted in descending order of `Match Score` (`V`)
    Internally uses ` Damerau-Levenshtein Edit Distance` to achieve Fuzzy search
    Output Results are at most 2 `Edit Distance` away from `keyword`

    :param keyword: for fuzzy search
    :return:        output dictionary list in descending order of `Match Score`
    """
    try:
        request_body = get_request_body(keyword)
        output_dict_list = []
        scroller = es_helpers.scan(es_client,
                                   query=request_body,
                                   scroll='1m',
                                   raise_on_error=False,
                                   preserve_order=True,
                                   size=1000,
                                   request_timeout=60,
                                   index=es_index,
                                   doc_type=es_doc_type)
        print request_body
        # Scrolling Output and storing it to List
        for es_output in scroller:
            print es_output
            score = es_output["_score"]
            source = es_output["_source"]
            source["score"] = score
            output_dict_list.append(source)
        return output_dict_list

    except Exception as err:
        print err.message, traceback.format_exc()


def get_request_body(keyword):
    """
    Creates Elasticsearch raw query to match provided keyword
    Output Results are at most 2 `Levenshtein Edit Distance` away from `keyword` (`fuzziness` -> 2)

    :param keyword:
    :return:
    """
    if len(keyword) >= 3:
        fuzziness_param = 2
    else:
        fuzziness_param = 'AUTO'

    request_body = {
          "query": {
            "match": {
              "search_term": {
                "query": keyword,
                "fuzziness": fuzziness_param,
                "prefix_length": 0
              }
            }
          }
        }
    return request_body

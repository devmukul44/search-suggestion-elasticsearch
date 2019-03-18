from elasticsearch import Elasticsearch
from elasticsearch import helpers as es_helpers
import traceback
import json

from config import es_host, es_port, es_index, es_doc_type

# Elasticsearch Configuration Constants
es_bulk_index_flag = 1000
es_client = Elasticsearch([es_host], port=es_port)

# Raw Files Path Constants
es_mapping_path = '../static/es_mapping.json'
data_raw_file_path = '../static/sample.learn.logs.2016.json'

try:
    # Pushing Index Mapping to Elasticsearch
    with open(es_mapping_path, 'r') as mapping_file:
        mapping_data = mapping_file.read()
        mapping_document = json.loads(mapping_data)
        es_client.indices.create(index=es_index, body=mapping_document)

    # Reading Data from Raw File
    lines = [line.rstrip('\n') for line in open(data_raw_file_path)]
    actions = []

    # Indexing Data to Elasticsearch using Bulk API
    for row in lines:
        cleaned_dict = json.loads(row)
        # Indexing only `result_type` -> `SR`
        if cleaned_dict["result_type"] == "SR":
            actions.append({
                "_op_type": "index",
                "_index": es_index,
                "_type": es_doc_type,
                "_source": cleaned_dict
            })
        if len(actions) == es_bulk_index_flag:
            print es_helpers.bulk(es_client, actions, index=es_index, doc_type=es_doc_type, request_timeout=60)
            actions = []
    if actions:
        print es_helpers.bulk(es_client, actions, index=es_index, doc_type=es_doc_type, request_timeout=60)

except Exception as err:
    print err.message, traceback.format_exc()

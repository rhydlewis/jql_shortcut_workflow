#!/usr/bin/python
# encoding: utf-8

import sys
import argparse
import urllib

from workflow import Workflow3, ICON_WEB, ICON_ERROR
KEY = 'historic_queries'
SUFFIX = "/issues/?jql="
SERVER = 'server'
log = None


def main(wf):
    # wf.open_log()
    log.info(wf.args)
    parser = argparse.ArgumentParser()
    parser.add_argument('--find-matching-queries', dest='find_queries')
    parser.add_argument('--delete-query', dest='delete_query')
    parser.add_argument('--store-query', dest='store_query')
    parser.add_argument('--print-queries', dest='print_query', action='store_true')
    parser.add_argument('--set-server', dest='server')
    args = parser.parse_args(wf.args)

    if args.find_queries:
        try:
            find_matching_queries(wf, args.find_queries)
        except ValueError as e:
            wf.add_item(title=e.message, subtitle=u'Missing configuration', icon=ICON_ERROR)
            wf.send_feedback()

    if args.delete_query:
        delete_query(wf, args.delete_query)

    if args.store_query:
        store_query(wf, args.store_query)

    if args.print_query:
        print_queries(wf)

    if args.server:
        set_server(wf, args.server)


def find_matching_queries(wf, search_string):
    filtered_queries = None

    url = get_url(wf)

    # historic_queries = wf.stored_data(KEY)
    #
    # if search_string and historic_queries:
    #     log.info("Found {0} possible matches: {1}".format(len(historic_queries), historic_queries))
    #     filtered_queries = wf.filter(search_string, historic_queries)

    filtered_queries = filter_queries(wf, search_string)

    if not filtered_queries:
        filtered_queries = [search_string]

    for query in filtered_queries:
        create_query_item(wf, url, query)

    wf.send_feedback()


def delete_query(wf, query):
    queries = wf.stored_data(KEY)
    query = clean_query(wf, query)
    queries.remove(query)
    wf.store_data(KEY, queries, serializer='json')


def filter_queries(wf, search_string):
    filtered_queries = wf.stored_data(KEY)

    if search_string and filtered_queries:
        filtered_queries = wf.filter(search_string, filtered_queries)
        log.info("Found {0} possible matches: {1}".format(len(filtered_queries), filtered_queries))

    return filtered_queries


def store_query(wf, store_query):
    query = clean_query(wf, store_query)
    log.info("Storing {0}".format(query))

    queries = wf.stored_data(KEY)
    if not queries:
        queries = []

    if query not in queries:
        queries.append(urllib.unquote(query))
        log.info("Stored query {0} in {1}".format(query, queries))
        wf.store_data(KEY, queries, serializer='json')

    log.info("Total historic queries is {0}: {1}".format(len(queries), queries))


def clean_query(wf, query):
    query = query.replace(get_url(wf), "")
    query = urllib.unquote(query)
    return query


def print_queries(wf):
    for query in wf.stored_data(KEY):
        log.info(query)


def create_query_item(wf, url, query):
    title = query
    subtitle = "Open \"" + url + query + "\""
    arg = url + (urllib.quote(query))

    wf.add_item(title=title, subtitle=subtitle, icon=ICON_WEB, arg=arg, valid=True)


def set_server(wf, server):
    if SUFFIX not in server:
        server = server + SUFFIX
        wf.settings[SERVER] = server


def get_url(wf):
    url = wf.settings.get(SERVER)
    if url is None:
        raise ValueError("Jira server URL not set, add it with 'set-jql-server'")
    return url


if __name__ == '__main__':
    workflow = Workflow3()
    log = workflow.logger
    sys.exit(workflow.run(main))
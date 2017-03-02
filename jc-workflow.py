#!/usr/bin/python
# encoding: utf-8

import sys
import argparse
import urllib

from workflow import Workflow3, ICON_WEB, ICON_ERROR

JIRA_KEY = 'jira_historic_queries'
JIRA_SUFFIX = "/issues/?jql="
JIRA_SERVER = 'jira-server'

CONFLUENCE_KEY = 'confluence_historic_queries'
CONFLUENCE_SUFFIX = "/dosearchsite.action?queryString="
CONFLUENCE_SERVER = 'confluence-server'

log = None


def main(wf):
    log.info(wf.args)
    parser = argparse.ArgumentParser()
    parser.add_argument('--find-matching-queries', dest='find_queries')
    parser.add_argument('--delete-query', dest='delete_query')
    parser.add_argument('--store-query', dest='store_query')
    parser.add_argument('--print-queries', dest='print_query', action='store_true')
    parser.add_argument('--set-server', dest='server')

    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--jira', dest='is_jira', action='store_true')
    feature_parser.add_argument('--confluence', dest='is_jira', action='store_false')
    parser.set_defaults(is_jira=True)

    args = parser.parse_args(wf.args)

    if args.find_queries:
        try:
            find_matching_queries(wf, args.find_queries, args.is_jira)
        except ValueError as e:
            wf.add_item(title=e.message, subtitle=u'Missing configuration', icon=ICON_ERROR)
            wf.send_feedback()

    if args.delete_query:
        delete_query(wf, args.delete_query, args.is_jira)

    if args.store_query:
        store_query(wf, args.store_query, args.is_jira)

    if args.print_query:
        print_queries(wf, args.is_jira)

    if args.server:
        if args.is_jira:
            set_server(wf, args.server, JIRA_SUFFIX, JIRA_SERVER)
        else:
            set_server(wf, args.server, CONFLUENCE_SUFFIX, CONFLUENCE_SERVER)


def find_matching_queries(wf, search_string, is_jira):
    filtered_queries = None

    url = get_url(wf, is_jira)

    filtered_queries = filter_queries(wf, search_string, is_jira)

    if not filtered_queries:
        filtered_queries = [search_string]

    for query in filtered_queries:
        create_query_item(wf, url, query)

    wf.send_feedback()


def delete_query(wf, query, is_jira):
    key = get_key(is_jira)
    queries = wf.stored_data(key)
    query = clean_query(wf, query, is_jira)
    queries.remove(query)
    wf.store_data(key, queries, serializer='json')


def filter_queries(wf, search_string, is_jira):
    filtered_queries = wf.stored_data(get_key(is_jira))
    if search_string and filtered_queries:
        filtered_queries = wf.filter(search_string, filtered_queries)
        log.info("Found {0} possible matches: {1}".format(len(filtered_queries), filtered_queries))

    return filtered_queries


def store_query(wf, store_query, is_jira):
    query = clean_query(wf, store_query, is_jira)
    log.info("Storing {0}".format(query))

    key = get_key(is_jira)

    queries = wf.stored_data(key)
    if not queries:
        queries = []

    if query not in queries:
        queries.append(urllib.unquote(query))
        log.info("Stored query {0} in {1}".format(query, queries))
        wf.store_data(key, queries, serializer='json')

    log.info("Total historic queries is {0}: {1}".format(len(queries), queries))


def clean_query(wf, query, is_jira):
    query = query.replace(get_url(wf, is_jira), "")
    query = urllib.unquote(query)
    return query


def print_queries(wf, is_jira):
    for query in wf.stored_data(get_key(is_jira)):
        log.info(query)


def create_query_item(wf, url, query):
    title = query
    subtitle = "Open \"" + url + query + "\""
    arg = url + (urllib.quote(query))

    wf.add_item(title=title, subtitle=subtitle, icon=ICON_WEB, arg=arg, valid=True)


def set_server(wf, server, suffix, key):
    if suffix not in server:
        server = server + suffix

    wf.settings[key] = server



def get_url(wf, is_jira):
    if is_jira:
        url = wf.settings.get(JIRA_SERVER)
        server_type = "Jira"
    else:
        url = wf.settings.get(CONFLUENCE_SERVER)
        server_type = "Confluence"

    if url is None:
        raise ValueError("{0} server URL not set".format(server_type))

    return url


def get_key(is_jira):
    if is_jira:
        key = JIRA_KEY
    else:
        key = CONFLUENCE_KEY

    return key


if __name__ == '__main__':
    workflow = Workflow3()
    log = workflow.logger
    sys.exit(workflow.run(main))

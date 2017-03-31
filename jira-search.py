import argparse
import sys
from workflow import Workflow3, ICON_WARNING
from lib.jira import JIRA
from config import PROJECT_KEY


def main(wf):
    log.debug('Started workflow')

    # get query
    args = parse_args()
    query = create_query(wf, args)

    # connect to jira
    jira = connect_to_jira(wf)

    # run query
    search_results = jira.search_issues(query)

    # per result, create feedback
    create_feedback(wf, jira, search_results)

    wf.send_feedback()


def create_feedback(wf, jira, issues):
    server = get_server(wf)

    if not len(issues):
        workflow.add_item('No results found', icon=ICON_WARNING)
        return

    for issue in issues:
        if issue.key:
            # full_story = jira.issue(issue.key)
            title = ', '.join([issue.key, issue.fields.summary])
            subtitle = ' - '.join([issue.fields.creator.displayName, issue.fields.project.name, issue.fields.status.name])
            arg = issue.permalink()
            wf.add_item(title=title, subtitle=subtitle, arg=arg, copytext=arg, valid=True)
                        # autocomplete=server + "/browse/" + issue.key,
                        # largetext=full_story.fields.description,


def connect_to_jira(wf):
    username = get_username(wf)
    keychain = get_keychain(wf)
    server = get_server(wf)
    if username and keychain and server:
        password = wf.get_password(account=username, service=keychain)
        auth = (username, password)
        return JIRA(server=server, basic_auth=auth)
    return None


def get_server(wf):
    server = wf.settings.get('server', None)
    return server


def get_keychain(wf):
    keychain = wf.settings.get('keychain', None)
    return keychain


def get_username(wf):
    username = wf.settings.get('user', None)
    return username


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--search-epics', dest='search_epic', nargs='?', default=None)
    parser.add_argument('-r', '--search-recently-modified', dest='search_recently_modified', nargs='?', default=None)
    parser.add_argument('-a', '--assigned-to-me', action='store_true')
    log.info(workflow.args)
    return parser.parse_args(workflow.args)


def create_query(wf, args):
    query = ""

    project = wf.settings.get(PROJECT_KEY, None)

    if project:
        query += "project = {0} and ".format(project)

    if args.search_epic:
        query += "issuetype = epic and text ~ \"{0}\" ".format(args.search_epic)

    if args.search_recently_modified:
        query += "text ~ \"{0}\" order by updatedDate DESC".format(args.search_epic)

    if args.assigned_to_me:
        query += "assignee = currentUser()"

    log.info(query)
    return query


if __name__ == '__main__':
    workflow = Workflow3()
    log = workflow.logger
    sys.exit(workflow.run(main))

#!/usr/bin/python
# encoding: utf-8

import sys
import argparse

from workflow import Workflow3
from lib.jira import JIRA

PROJECT_KEY = 'project'
JIRA_SERVER_KEY = 'jira-server'

log = None


def setup(wf):
    username = get_username(wf)
    keychain = get_keychain(wf)
    server = get_server(wf)
    project = get_project(wf)
    if username and keychain and server:
        password = wf.get_password(account=username, service=keychain)
        auth = (username, password)
        return JIRA(server=server, basic_auth=auth)
    return None


def get_project(wf):
    server = wf.settings.get(PROJECT_KEY, None)
    return server


def get_server(wf):
    server = wf.settings.get(JIRA_SERVER_KEY, None)
    return server


def get_keychain(wf):
    keychain = wf.settings.get('keychain', None)
    return keychain


def get_username(wf):
    username = wf.settings.get('user', None)
    return username


def main(wf):
    log.info(wf.args)
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', dest='server', nargs='?', default=None)
    parser.add_argument('--user', dest='user', nargs='?', default=None)
    parser.add_argument('--password', dest='password', nargs='?', default=None)
    parser.add_argument('--project', dest='project', nargs='?', default=None)

    args = parser.parse_args(wf.args)

    if args.server:# and 'http://' in args.server:
        log.info('Saving new server: ' + args.server)
        wf.settings[JIRA_SERVER_KEY] = args.server
        return 0

    if args.user:
        log.info('Saving new user: ' + args.user)
        wf.settings['user'] = args.user
        return 0

    if args.project:
        log.info('Saving new project: ' + args.project)
        wf.settings[PROJECT_KEY] = args.project
        return 0

    if args.password:
        username = wf.settings.get('user', None)
        if username:
            log.info('Setting the password')
            service = 'jira@alfred'
            wf.settings['keychain'] = service
            wf.save_password(username, args.password, service)
            return 0
        else:
            log.error('Error: User not set. The password was not stored')


if __name__ == '__main__':
    workflow = Workflow3()
    log = workflow.logger
    sys.exit(workflow.run(main))

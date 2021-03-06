#!/usr/bin/python3

"""
Close open github issues by searching for a string in the title.
This is useful for closing issues migrated from another repo which are prepended by '[CLOSED]', as caused by
https://github.com/IQAndreas/github-issues-import

Steven Eardley, Feb 2018.
"""

import requests
from util import rate_limited

API_BASE = 'https://api.github.com'
HEADER = {'Accept': 'application/vnd.github.v3+json'}


# First we get all of the issue numbers that fulfil our criteria
def search_issues_by_string(search_string, repo):
    query = 'q={0}+state:open+in:title+repo:{1}&per_page=100'.format(search_string, repo)
    next_req = requests.Request('GET', API_BASE + '/search/issues', params=query).prepare().url
    issue_nums = []
    while next_req is not None:
        resp = requests.get(next_req, headers=HEADER)
        issue_nums.extend([iss['number'] for iss in resp.json()['items']])
        next_req = resp.links.get('next', {}).get('url')
    return issue_nums


def match_all_issues(repo):
    next_req = requests.Request('GET', API_BASE + '/repos/{0}/issues'.format(repo)).prepare().url
    issue_nums = []
    while next_req is not None:
        resp = requests.get(next_req, headers=HEADER)
        issue_nums.extend([iss['number'] for iss in resp.json() if iss.get('pull_request') is None])
        next_req = resp.links.get('next', {}).get('url')
    return issue_nums


# Then close issues one-by one
@rate_limited(2.0)
def close_issue_by_number(num, repo):

    patch = {"state": "closed"}
    resp = requests.patch(API_BASE + '/repos/{0}/issues/{1}'.format(repo, num), headers=HEADER, json=patch)
    if resp.status_code == 200:
        print('Closed issue {0} in {1}.'.format(num, repo))
    else:
        print('Error closing issue {0} in {1}.'.format(num, repo))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--oauth', help='your OAuth2 token', required=True)
    parser.add_argument('-r', '--repo', help='repository to search', required=True)
    parser.add_argument('-s', '--search_string', help='the substring you want to match issues with', default='[closed]')
    parser.add_argument('-a', '--all_open', help="close all open issues (not PRs). Don't set -s.", action='store_true')
    args = parser.parse_args()

    HEADER['Authorization'] = 'Bearer ' + args.oauth

    if args.all_open:
        issues = match_all_issues(args.repo)
    else:
        issues = search_issues_by_string(args.search_string, args.repo)

    delete = input('{} issues found. Close these? [y/N]: '.format(len(issues)))
    if delete.lower() == 'y':
        [close_issue_by_number(i, args.repo) for i in issues]
        print('Done. You may need to re-run if there were more issues than the search was willing to return.')
    else:
        print('OK. No action.')

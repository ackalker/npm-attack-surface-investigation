#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
from time import sleep
import csv


HEADER = ["package_name", "package_url", "gist_dependencies", "repository_type",
          "repository_url", "weekly_downloads", "dependents",
          "contributors", "perc_participation", "commits"]

cwd = os.path.dirname(__file__)
OUTPUT_PATH = os.path.join(cwd, 'data')
INPUT_FILE = 'npm_packages_metadata'
OUTPUT_FILE = 'npm_packages_github_metadata'
# Regex templates
github_tpl_regex = re.compile('^https://github.com/(.+?)/([^/]+).*$')
last_page_tpl_regex = re.compile('^.*<(.*\?page=(\d+))>; rel="last".*$')
# Github api token
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN','GITHUB_TOKEN')


def compute_commits_and_perc_participation(r):
    """
    """
    perc_participation = 0
    data = r.json()
    commits_owner = sum(data['owner'])
    commits_all =  sum(data['all'])
    if commits_all != 0:
        perc_participation = (commits_all - commits_owner) * 100 / commits_all

    return commits_all, perc_participation


def get_commits_and_perc_participation(pkg):
    """
    Get the number of commmits and the percentage of participation using Github API v3
        - calculated as the overall commits over the overall commits minus the commits of the owner
    """
    participation = None

    # Github API v3 list of commits
    GITHUB_PARTICIPATION_API_TPL = "https://api.github.com/repos/%(owner)s/%(repo)s/stats/participation"
    url = GITHUB_PARTICIPATION_API_TPL % {'owner': pkg['owner'], 'repo': pkg['repo']}
    r = make_request(url,{'Authorization': 'token %s' % (GITHUB_TOKEN)})
    if r.status_code == 200:
        pkg['commits'], pkg['perc_participation'] = compute_commits_and_perc_participation(r)
    elif r.status_code == 202:
        success = False
        for i in range(1,6):
            r = make_request(url,{'Authorization': 'token %s' % (GITHUB_TOKEN)})
            if r.status_code == 200:
                pkg['commits'], pkg['perc_participation'] = compute_commits_and_perc_participation(r)
                success = True
                break
            sleep(i*2)
        if not success:
            print 'after 5 retries we could not get cached data for %s from github....desisting' % (
                pkg['repository_url'])
    else:
        print "unexpected status_code %s for repo %s" % (r.status_code, pkg['repository_url'])

    return pkg


def get_contributors(pkg):
    """
    Get the number of contributors using Github API v3
    """
    contributors = None

    # Github API v3 list of commits
    GITHUB_CONTRIB_API_TPL = "https://api.github.com/repos/%(owner)s/%(repo)s/contributors"
    url = GITHUB_CONTRIB_API_TPL % {'owner': pkg['owner'], 'repo': pkg['repo']}
    r = make_request(url,{'Authorization': 'token %s' % (GITHUB_TOKEN)})
    if r.status_code == 200:
        if 'link' in r.headers:
            m = last_page_tpl_regex.match(r.headers['link'])
            if m:
                url = m.group(1)
                r = make_request(url, {'Authorization': 'token %s' % (GITHUB_TOKEN)})
                if r.status_code == 200:
                    contributors = (int(m.group(2))-1)*30 + len(r.json())
                else:
                    print "unexpected status_code %s for repo %s" % (r.status_code, pkg['repository_url'])
        else:
            contributors = len(r.json())
        pkg['contributors'] = contributors
    else:
        print "unexpected status_code %s for repo %s" % (r.status_code, pkg['repository_url'])

    return pkg


def make_request(url, headers):
    """
    make an http request
    """
    r = None
    try:
        r = requests.get(url, headers=headers)
    except Exception as e:
        raise e
    return r


def get_npm_metadata_results():
    """
    get previously calculated npm metadata results
    """
    try:
        with open('%s/%s.csv' % (OUTPUT_PATH, INPUT_FILE), 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except IOError as e:
        return list()


def run():
    """
    main loop
    """
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    rows = get_npm_metadata_results()

    with open('%s/%s.csv' %
              (OUTPUT_PATH, OUTPUT_FILE), 'w') as fout:
        writer = csv.DictWriter(fout, fieldnames=HEADER, extrasaction='ignore')
        writer.writeheader()
        count = 0
        for row in rows:
            if row['repository_type'] == 'github':
                count +=1
                if (count % 50 == 0):
                    print('processed %s github repos' % (count))

                m = github_tpl_regex.match(row['repository_url'])
                if m:
                    row['owner'] = m.group(1)
                    row['repo'] = m.group(2)
                else:
                    print "could not extract owner and repo from github repo url %s" % (row['repository_url'])
                    continue
                row = get_contributors(row)
                row = get_commits_and_perc_participation(row)
                # row = get_commmit_activity(row)
            else:
                print 'repository type is not github for npm package %s' % (row['package_url'])
                row['contributors'] = None
                row['perc_participation'] = None
                row['commits'] = None
            writer.writerow(row)


if __name__ == '__main__':
    # Parse command-line arguments.
    run()
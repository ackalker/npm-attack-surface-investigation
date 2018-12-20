#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import os
import re
import requests
from bs4 import BeautifulSoup
import datetime
from time import sleep
import csv


URL_MOST_DEPENDENT_LIBRARIES = "https://gist.githubusercontent.com/anvaka/8e8fa57c7ee1350e3491/raw/27c81e27e0ebd7331db1fd1ecf14f2179530c083/01.most-dependent-upon.md"
HEADER = ["package_name", "package_url", "gist_dependencies", "repository_type",
          "repository_url", "weekly_downloads", "dependents"]

cwd = os.path.dirname(__file__)
OUTPUT_PATH = os.path.join(cwd, 'data')
DATA_FILE = 'npm_packages_metadata'
# Regex templates
gist_tpl_regex = re.compile('^\d+\.\s\[(.*)\]\((.*)\)\s*-\s*(\d+).*$')
dependents_tpl_regex = re.compile('^\?activeTab=dependents$')
github_tpl_regex = re.compile('^https://github.com/[^#]+$')


def get_most_dependent_libraries():
    """
    Get the most depended upon libraries from a public gist that relies on a cron job
    https://gist.github.com/anvaka/8e8fa57c7ee1350e3491
    """
    try:
        response = requests.get(URL_MOST_DEPENDENT_LIBRARIES)
        lines = response.content.split("\n")
        return lines
    except Exception as e:
        print "could not retrieve libraries from gist"
        raise e


def transform_md_file(lines):
    """
    transform markdown file into a list of valid rows and initialize each row with global constants
    """
    data = []
    for line in lines:
        row={'low_maintenance_boundary': COMMITS_BOUNDARY,
             'days_delta': DAYS_DELTA}
        m =gist_tpl_regex.match(line)
        if m:
            row['package_name'] = m.group(1)
            row['package_url'] = m.group(2)
            row['gist_dependencies'] = m.group(3)
            data.append(row)
    return data


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


def scrape_npm_metadata(pkg):
    """
    Get package metadata from the package npm page
        - Dependents
        - Weekly downloads
        - Repository url
    """
    r = make_request(pkg['package_url'], None)
    # If we receive a too many requests status code sleep for 5 minutes since
    # the site does not provide a Retry-after header and retry one more time
    if r.status_code == 429:
        sleep(5*60)
        r = make_request(pkg['package_url'], None)
    soup = BeautifulSoup(r.content, 'html.parser')
    # Get dependents metadata
    dep_meta = soup.find('a', href=dependents_tpl_regex).find('span', class_='tabs__number___VComN')
    if dep_meta:
        pkg['dependents'] = int(dep_meta.text.replace(',',''))

    # Get weekly downloads
    dl_meta = soup.find('p', class_='package__counter___2s5Ci')
    if dl_meta:
        pkg['weekly_downloads'] = int(dl_meta.text.replace(',',''))
    # Get github repo
    gh_url = soup.find('a', class_='package__sidebarLink___zE7yA', href=github_tpl_regex)
    if gh_url:
        pkg['repository_type'] = 'github'
        pkg['repository_url'] = gh_url['href']
    else:
        pkg['repository_type'] = 'unknown'
        pkg['repository_url'] = None
    return pkg

def get_previous_results():
    """
    get previous results and use them as a cache as a polite gesture to npm servers
    you can use the --no-cache flag to start fresh instead
    """
    try:
        with open('%s/%s.csv' % (OUTPUT_PATH, DATA_FILE), 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except IOError as e:
        return list()


def run(args):
    """
    main loop
    """
    prev_rows = []
    cache = set()
    # Restore cached package metadata if available and not overwritten by flag
    if not args.no_cache:
        prev_rows = get_previous_results()
        cache = set([r['package_name'] for r in prev_rows])

    # Get investigation libraries from original gist
    # TODO: improve source by directly hitting the npm registry?
    libraries_md = get_most_dependent_libraries()
    # Transform from markdown to list of valid rows
    packages = transform_md_file(libraries_md)

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    with open('%s/%s.csv' %
              (OUTPUT_PATH, DATA_FILE), 'w') as fout:
        writer = csv.DictWriter(fout, fieldnames=HEADER, extrasaction='ignore')
        writer.writeheader()
        # Write previous rows if available and we are using cache
        writer.writerows(prev_rows)
        count = 0
        for pkg in packages:
            if pkg['package_name'] in cache:
                continue

            count +=1
            pkg = scrape_npm_metadata(pkg)
            cache.add(pkg['package_name'])
            writer.writerow(pkg)

            if (count % 10 == 0):
                print('processed %s npm packages' % (count))
            sleep(1.2)


if __name__ == '__main__':
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        description="Analize npm package data")
    parser.add_argument('--no-cache',
                        dest='no_cache',
                        action='store_true')
    args = parser.parse_args()
    run(args)
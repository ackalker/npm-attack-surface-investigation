npm-attack-surface-investigation
================================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [Installation](#installation)
* [Run project](#run-project)

What is this?
-------------

A repository created for an investigation treating OSS maintenance burnout as an attack surface following the [events](https://github.com/dominictarr/event-stream/issues/116) that were revealed on the `event-stream` npm package

We wanted to investigate if the attack above could be potentially replicated to some of the most used/depended upon npm packages.

We grab the top 1000 npm packages that other projects rely upon and then scrape [https://npmjs.com](https://npmjs.com) metadata including weekly downloads and dependents.

Finally using github API we check the commit activity on the source repo checking for low maintenance clues, such as less than 5 commits in the past year, the contributors list and the percentage of commits done by people other than the owner.

This codebase is licensed under the MIT open source license. See the [LICENSE](LICENSE) file for the complete license.


Assumptions
-----------

* You are using Python 2.7. (Probably the version that came OSX.)
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.


Installation
------------

```
cd npm-attack-surface-investigation
mkvirtualenv npm-attack-surface-investigation
pip install -r requirements.txt
```

Run Project
-----

Make sure the virtualenv is activated, if it is not run `workon npm-attack-surface-investigation`.

1. Run the script that grabs the GIST most depended upon NPM libraries and then scrapes its metadata from npmjs.org
	`python scrape_npm_metadata.py`

	The results are stored in `data/npm_packages_metadata.csv`

2. Run the script that enriches the previous csv to include github api data using the repository url
	`python get_github_api_data`

	The results are stored in `data/npm_packages_github_metadata.csv`

*NOTE:* Sometimes the stats from github are not readily available so if you see messages on the console you may need to run the script again leaving a few minutes for the stats to be calculated on github side (via: https://developer.github.com/v3/repos/statistics/#a-word-about-caching)
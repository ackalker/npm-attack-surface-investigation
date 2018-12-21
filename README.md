npm-attack-surface-investigation
================================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [Installation](#installation)
* [Run project](#run-project)

What is this?
-------------

A repository created for an investigation treating OSS maintenance burnout as an attack surface following the [attack](https://github.com/dominictarr/event-stream/issues/116) that was revealed recently on the `event-stream` npm package

We wanted to investigate if the attack was a one of a kind or on the contrary if it could be potentially replicated to some of the most used/depended upon npm packages.

We grabbed the top 1000 npm packages that other projects rely upon and then scrape [https://npmjs.com](https://npmjs.com) metadata including weekly downloads and dependents.

Finally using github API we obtained the commit activity on the source repo checking for low maintenance clues, such as less than 5 commits in the past year, the contributors list and the percentage of commits done by people other than the owner.

This codebase is licensed under the MIT open source license. See the [LICENSE](LICENSE) file for the complete license.

This investigation was conducted by TEGRA.

TEGRA is an R&D Cybersecurity Center based in Galicia (Spain). It is a joint effort from Telefónica, a leading international telecommunications company, through ElevenPaths, its global cybersecurity unit, and Gradiant, an ICT R&D center with more than 100 professionals working in areas like connectivity, security and intelligence, to create innovative products and services inside cybersecurity.

TEGRA's work is focused on two areas within the cybersecurity landscape: Data Security and Security Analytics. We are committed to creating state-of-the-art technologies that can nurture and thus provide differentiating value to our products.


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
-----------

Make sure the virtualenv is activated, if it is not run `workon npm-attack-surface-investigation`.

1. Run the script that grabs the GIST most depended upon NPM libraries and then scrapes its metadata from npmjs.org
	
	`$ python scrape_npm_metadata.py`

	The results are stored in `data/npm_packages_metadata.csv`

2. Run the script that enriches the previous csv to include github api data using the repository url
	
	`$ python get_github_api_data.py`

	The results are stored in `data/npm_packages_github_metadata.csv`

*NOTE:* Sometimes the stats from github are not readily available so if you see messages on the console you may need to run the script again leaving a few minutes for the stats to be calculated on github side (via: https://developer.github.com/v3/repos/statistics/#a-word-about-caching)

Contributors
------------

See the [CONTRIBUTORS](CONTRIBUTORS) file.

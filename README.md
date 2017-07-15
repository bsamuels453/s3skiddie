# s3skiddie

Perform black box penetration tests against AWS S3 buckets. Discover bad permissions, explore bucket contents, discover sensitive files.

## Features

* Enumerate bucket contents
* Build local copy of bucket structure for easy analysis
* Flag sensitive files discovered in bucket index
* Test bucket read permission
* Test bucket write permission
* Test bucket read ACL permission
* Test object read ACL permission
* Test object read permission
* Test multiple buckets at a time

## Installation

1. ``git clone https://github.com/bsamuels453/s3skiddie.git``
2. ``cd s3skiddie``
3. ``python3 ./setup.py install``

## Usage

todo: this section

until then, read the help page

``s3skiddie -h``

## Requirements

* Python 3
* beautifulsoup4
* tldextract
* tabulate
* clint
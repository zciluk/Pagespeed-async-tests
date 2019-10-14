# Pagespeed performance tests app

App written in Python to perform quick async performance tests on chosen sitemap using Google's Pagespeed API.
Features:

- add custom sitemap
- run tests asynchronically (faster tests for big sitemaps)
- generate a test report with average values summary

## Instalation

Make sure you have python3 installed -> https://www.python.org/download/releases/3.0/
Check it by running command:

```sh
$ python3 --version
```

Then, in main folder of the app run command:

```sh
$ pip install octopus-http
```

After octopus is installed, you can run application using command:

```sh
$ python3 pagespeed-tests.py
```

## API key

For making multiply requests per minute, you will need an Google API key, that can be generated here (Acquiring and using an API key):
https://developers.google.com/speed/docs/insights/v5/get-started
After it is generated, you can paste it into the `apiKey` variable.

## Configuration variables

By default, project is configured to test performance of www.trello.com website. You can configure it for own purposes:
`projectName` - name of the project that will be written in results file title
`sitemapFile` name of the sitemap placed in /sitemaps/ catalogue that will be read by app. Each line of the file should be a new address.
`apiKey` API key from previous paragraph goes here. If empty, there can be limitations to simultaneous requests.
`strategy` if empty - desktop. Can be set to either 'mobile' or 'desktop'. Mobile results are artificaly throttled to simulate slow device.
`categories` for now - please does not change 😅
`threadsNumber` number of requests sent asynchronically at once

## Ideas & Todos

🚀 fix numeration of results

🚀 make it more configurable (categories)

🚀 support xml sitemaps

🚀 upload the results to specific location

🚀 graphicially formated results (xls, html?)

🚀 compare results in time (graphs)

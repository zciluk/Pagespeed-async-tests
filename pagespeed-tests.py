import json
import datetime
from pprint import pprint
from octopus import Octopus
import pathlib

#globalne
projectName = 'trello' #project name - result file with have this name
sitemapFile = 'sitemap.txt' #file with sitemap (links in each line)
apiKey =  'AIzaSyCXxFK9edUTCVmpU8LxE5FY0K6BWnMZNbI' #api key generated here https://developers.google.com/speed/docs/insights/v5/get-started. If deleted - API request limit can be easliy breached
strategy = 'desktop' #mobile OR desktop
categories = ['performance', 'seo', 'accessibility', 'best-practices'] #categories to be tested and saved to file. These can be 'performance', 'seo', 'accessibility', 'best-practices'
threadsNumber = 15 #number of requests sent asynchronically at once


startTime = datetime.datetime.now()        
print(f'Starting process - {startTime.strftime("%H:%M")}')
pathlib.Path('./results').mkdir(parents=True, exist_ok=True)  #create results fir if not exists
resultFile = open(f'./results/{projectName}-{strategy} performance-{startTime.strftime("%d-%m-%Y_%H:%M:%S")}.csv', 'w')
columnNames = "Number, URL, First Contentful Paint, First Interactive, Performance, SEO, Accessibility, Best-Practices\n"
resultFile.write(columnNames)


# settings for octopus threads

otto = Octopus(
    concurrency=threadsNumber, auto_start=True, cache=True,
    request_timeout_in_seconds=30
)

def handle_url_response(url, response):
    number = url.split('&num=')
    splitUrl = url.split('?url=') 
    reqUrl =  splitUrl[1].split('&strategy=')
    row = f'{number[1]}'
    try:
        parsedResponse = json.loads(response.text)
        contentfulPaint = parsedResponse['lighthouseResult']['audits']['first-contentful-paint']['displayValue'] 
        firstInteractive = parsedResponse['lighthouseResult']['audits']['interactive']['displayValue']
        performanceScore = parsedResponse['lighthouseResult']['categories']['performance']['score']
        seoScore = parsedResponse['lighthouseResult']['categories']['seo']['score']
        accessScore = parsedResponse['lighthouseResult']['categories']['accessibility']['score']
        practicesScore = parsedResponse['lighthouseResult']['categories']['best-practices']['score']
        
    except KeyError:
        print(f'Error: Specific key not found for {url}. Maybe internal server error or limit error')
        return
    except TimeoutError:
        print(f'Error: Timeout for url: {url}.')    
        
    try:
        row = f'{number[1]},{reqUrl[0]},{contentfulPaint},{firstInteractive},{performanceScore},{seoScore},{accessScore}'
        row += f',{practicesScore}\n'
        resultFile.write(row)
    except NameError:
        print(f'Error: Error writing file {url}.')
        return
        
    try:
        print(f'DONE { number[1]}/{num}, Performance - {performanceScore} / {reqUrl[0]}')
    except NameError:
        print(f'Error: Name error for {url}.') 
        return   



sitemap = open(sitemapFile).readlines()
sitemap = [line.rstrip('\n') for line in sitemap]
for num,line in enumerate(sitemap, start=1):
        if num==1:
            print(f'Processing {len(sitemap)} requests')
        # If no "strategy" parameter is included, the query by default returns desktop data.
        url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={line}&strategy={strategy}'
        for cat in categories:
            url += f'&category={cat}'
        if apiKey:
            url += f'&key={apiKey}'

        url +=f'&num={num}'
        otto.enqueue(url, handle_url_response)

otto.wait(timeout=0)  # waits until queue is empty or timeout is ellapsed
finishTime = datetime.datetime.now()
completionTime = finishTime - startTime    
print(f'FINISHED - {finishTime.strftime("%H:%M")}. Took {completionTime.seconds//3600}:{(completionTime.seconds//60)%60}:{(completionTime.seconds%3600)%60}' )
resultFile.close()
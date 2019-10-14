import json
import datetime
from octopus import Octopus
import pathlib

#config variables
projectName = 'trello' #project name - result file with have this name
sitemapFile = 'trello.txt' #file with sitemap (links in each line)
apiKey =  '' #api key generated here https://developers.google.com/speed/docs/insights/v5/get-started. If deleted - API request limit can be easliy breached
strategy = 'mobile' #mobile OR desktop
categories = ['performance', 'seo', 'accessibility', 'best-practices'] #categories to be tested and saved to file. These can be 'performance', 'seo', 'accessibility', 'best-practices'
threadsNumber = 15 #number of requests sent asynchronically at once


startTime = datetime.datetime.now()        
print(f'Starting process - {startTime.strftime("%H:%M")}')
pathlib.Path('./results').mkdir(parents=True, exist_ok=True)  #create results fir if not exists
filePath = f'./results/{projectName}-{strategy} performance-{startTime.strftime("%d-%m-%Y_%H:%M:%S")}.csv'
resultsFile = open(filePath, 'w')
columnNames = "Number, URL, First Contentful Paint, First Interactive, Performance, SEO, Accessibility, Best-Practices\n"
resultsFile.write(columnNames)


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
        resultsFile.write(row)
    except NameError:
        print(f'Error: Error writing file {url}.')
        return
        
    try:
        print(f'DONE { number[1]}/{num}, Performance - {performanceScore} / {reqUrl[0]}')
    except NameError:
        print(f'Error: Name error for {url}.') 
        return   



sitemap = open(f'./sitemaps/{sitemapFile}').readlines()
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
print(f'Adding summary...' )
resultsFile.close()
getSummary = open(filePath, 'r').readlines()
getSummary = [line.rstrip('\n') for line in getSummary]
accContentfulPaint = accFirstInteractive = accPerformance = accSeo = accAccessability = accBestPractices = 0
sumResults = len(getSummary) - 1
for num,line in enumerate(getSummary, start=1):
        if num==1:
            continue
        line = line.split(',')
        accContentfulPaint += float(line[2][:-2])
        accFirstInteractive += float(line[3][:-2])
        accPerformance += float(line[4])
        accSeo += float(line[5])
        accAccessability += float(line[6])
        accBestPractices += float(line[7])

updateSummary = open(filePath, 'a')
updateSummary.write("\n")
updateSummary.write("Total,  ,  Average First Contenful , Average First Interactive , Average Performance, Average SEO, Average Accessibility, Average Best-Practices\n")
updateSummary.write(f'{sumResults},--,{"{0:.2f}".format(accContentfulPaint/sumResults)},{"{0:.2f}".format(accFirstInteractive/sumResults)},{"{0:.2f}".format(accPerformance/sumResults)},{"{0:.2f}".format(accSeo/sumResults)},{"{0:.2f}".format(accAccessability/sumResults)},{"{0:.2f}".format(accBestPractices/sumResults)}')
updateSummary.close()
finishTime = datetime.datetime.now()
completionTime = finishTime - startTime    
print(f'FINISHED - {finishTime.strftime("%H:%M")}. Took {completionTime.seconds//3600}:{(completionTime.seconds//60)%60}:{(completionTime.seconds%3600)%60}' )

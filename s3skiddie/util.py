import urllib.request

useragent = ""



def buildRequest(url, data=None, method="GET"):
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36' + "" + useragent
        }
    )
    return req

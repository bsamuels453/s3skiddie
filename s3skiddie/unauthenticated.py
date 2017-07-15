import urllib
import urllib.parse
import bs4, errno, time
from clint.textui import puts, colored, indent, progress
from s3skiddie.util import buildRequest
from socket import error as socket_error

def getBucketRegion(bucketname, counter=0):
    if(len(bucketname) < 3):
        puts(colored.red("Invalid bucket; bucket names must be at least 3 characters long."))
        return None
    default_region = "s3-us-west-2"
    url = "https://" + default_region + ".amazonaws.com/" + bucketname + "/"
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
            #no error? we guessed the region correctly

            return default_region
    except urllib.error.HTTPError as error:
        soup = bs4.BeautifulSoup(error.read().decode("UTF-8"), "html.parser")
        errorCode = soup.error.code.get_text()
        if errorCode == "PermanentRedirect":

            endpoint = soup.error.endpoint.get_text()
            #print(endpoint)
            region = endpoint.split(".")[-3]

            #check for regionless bucket
            if region == "amazonaws":
                return "s3"
            else:
                return region
        elif errorCode == "NoSuchBucket":
            return None
        elif errorCode == "AccessDenied":
            return default_region
        elif errorCode == "AllAccessDisabled":
            return default_region
        else:
            assert(False)
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            raise serr
        if counter>=5:
            puts(colored.red("Connection refused 5 times in a row. go figure."))
            raise serr
        puts(colored.yellow("Connection refused, trying again in 1 second"))
        time.sleep(1)
        return getBucketRegion(bucketname, counter+1)

def listBucketContents(bucketname, region,marker=None, markercount=0):
    if marker is None:
        url = "https://" + region + ".amazonaws.com/" + bucketname + "/"
    else:
        url = "https://" + region + ".amazonaws.com/" + bucketname + "/?marker=" + urllib.parse.quote(str(marker))
    try:
        req = buildRequest(url)
        with urllib.request.urlopen(req) as response:
            soup = bs4.BeautifulSoup(response.read().decode("UTF-8"), "html.parser")

            objects = []
            for contents in soup.listbucketresult.find_all("contents"):
                objects.append(contents.key.get_text())

            if soup.listbucketresult.istruncated.get_text() == "true":
                marker = objects[-1]
                puts(colored.white("There are more than " + str(markercount*1000 + 1000) + " objects in bucket index."))
                restOfObjects = listBucketContents(bucketname, region, marker, markercount+1)
                objects = list(set(objects + restOfObjects))


            return objects
    except urllib.error.HTTPError as error:
        soup = bs4.BeautifulSoup(error.read().decode("UTF-8"), "html.parser")
        if soup.error.code.get_text() == "AccessDenied" or soup.error.code.get_text() == "AllAccessDisabled":
            return (None)
        else:
            assert(False)


def getBucketACL(bucketname, region):
    url = "https://" + region + ".amazonaws.com/" + bucketname + "/?acl"
    try:
        req = buildRequest(url)
        with urllib.request.urlopen(req) as response:
            soup = bs4.BeautifulSoup(response.read().decode("UTF-8"), "html.parser")

            grants = []
            for grant in soup.accesscontrolpolicy.accesscontrollist.find_all("grant"):
                grants.append(grant)

            return (grants)
    except urllib.error.HTTPError as error:
        soup = bs4.BeautifulSoup(error.read().decode("UTF-8"), "html.parser")
        if soup.error.code.get_text() == "AccessDenied" or soup.error.code.get_text() == "AllAccessDisabled":
            return (None)
        else:
            assert(False)

def getObject(bucketname, region, object):
    url = "https://" + region + ".amazonaws.com/" + bucketname + "/" + urllib.parse.quote_plus(object)
    try:
        req = buildRequest(url)
        with urllib.request.urlopen(req) as response:
            data = response.read()
            return data

    except urllib.error.HTTPError as error:
        soup = bs4.BeautifulSoup(error.read().decode("UTF-8"), "html.parser")
        if soup.error.code.get_text() == "AccessDenied" or soup.error.code.get_text() == "AllAccessDisabled":
            return None
        else:
            print(str(soup.error))
            assert(False)
    except urllib.error.URLError:
        puts(colored.red("Connection reset, retrying..."))
        return getObject(bucketname, region, object)

def getObjectACL(bucketname, region, object):
    url = "https://" + region + ".amazonaws.com/" + bucketname + "/" + urllib.parse.quote_plus(object) + "?acl"
    try:
        req = buildRequest(url)
        with urllib.request.urlopen(req) as response:
            soup = bs4.BeautifulSoup(response.read().decode("UTF-8"), "html.parser")

            grants = []
            for grant in soup.accesscontrolpolicy.accesscontrollist.find_all("grant"):
                grants.append(grant)

            return (grants)

    except urllib.error.HTTPError as error:
        soup = bs4.BeautifulSoup(error.read().decode("UTF-8"), "html.parser")
        if soup.error.code.get_text() == "AccessDenied"  or soup.error.code.get_text() == "AllAccessDisabled":
            return None
        else:
            assert(False)
    except urllib.error.URLError:
        puts(colored.red("Connection reset, retrying..."))
        return getObjectACL(bucketname, region, object)

def writeTestObject(bucketname, region, objectname, objectcontent):
    url = "https://" + region + ".amazonaws.com/" + bucketname + "/" + urllib.parse.quote_plus(objectname)

    req = buildRequest(url, data=objectcontent.encode("UTF-8"), method='PUT')
    try:
        r = urllib.request.urlopen(req)
        return r.read()

    except urllib.error.HTTPError as error:
        soup = bs4.BeautifulSoup(error.read().decode("UTF-8"), "html.parser")
        if soup.error.code.get_text() == "AccessDenied"  or soup.error.code.get_text() == "AllAccessDisabled":
            return None
        else:
            print(str(soup.error))
            assert(False)

def writeBucketAcl(bucketname, region, cannedAcl):
    url = "https://" + region + ".amazonaws.com/" + bucketname + "/?acl"
    req = urllib.request.Request(url, method='PUT')
    req.add_header("x-amz-acl",cannedAcl)

    try:
        r = urllib.request.urlopen(req)
        return r.read()

    except urllib.error.HTTPError as error:
        soup = bs4.BeautifulSoup(error.read().decode("UTF-8"), "html.parser")
        if soup.error.code.get_text() == "AccessDenied"  or soup.error.code.get_text() == "AllAccessDisabled":
            return None
        else:
            print(str(soup.error))
            assert(False)

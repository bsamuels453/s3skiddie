import tabulate
import os.path
from clint.textui import puts, colored, indent, progress
import string, shutil
from s3skiddie.buildtree import buildtree


def writeIndexReadResults(path, results):
    filepath = os.path.join(path, "index-read-results.txt")
    file = open(filepath, "w")

    toWrite = []
    for result in results:
        if result["region"] is None or result["objects"] is None:
            continue
        url = "https://" + result["bucket"] + "." + result["region"] + ".amazonaws.com/"
        if result["objects"]["testresult"] == "pass":
            toWrite.append("s3://" + result["bucket"] + "  :  Index permission denied.")
        else:
            objects = result["objects"]["testdata"]
            toWrite.append("s3://" + result["bucket"] + "  :  " + str(len(objects)) + " objects found in index.")
            for object in objects:
                toWrite.append("    " + url + object)

    file.write("\n".join(toWrite))
    file.close()
    #puts(colored.white("Index read results written to " + filepath))

def writeReadAclResults(path, results):
    filepath = os.path.join(path, "read-bucket-acl-results.txt")
    file = open(filepath, "w")

    toWrite = []
    for result in results:
        if result["region"] is None or result["bucketacl"] is None:
            continue

        if result["bucketacl"]["testresult"] == "pass":
            toWrite.append("s3://" + result["bucket"] + " : Permission denied for reading bucket ACL.")
        else:
            grants = result["bucketacl"]["testdata"]
            toWrite.append("s3://" + result["bucket"] + " : " + str(len(grants)) + " publicly readable ACL grants found.")
            for grant in grants:
                toWrite.append("    " + str(grant))

    file.write("\n".join(toWrite))
    file.close()
    #puts(colored.white("Bucket ACL read results written to " + filepath))


def writeReadObjectsResult(path, results):
    filepath = os.path.join(path, "read-objects-results.txt")
    file = open(filepath, "w")

    toWrite = []
    for result in results:
        if result["region"] is None or result["readableObjects"] is None:
            continue

        if result["readableObjects"]["testresult"] == "pass":
            toWrite.append("s3://" + result["bucket"] + " : Permission denied for reading all objects in bucket.")
        else:
            readableObjects = result["readableObjects"]["testdata"]
            numTotalObjects = len(result["objects"]["testdata"])
            toWrite.append("s3://" + result["bucket"] + " : " + str(len(readableObjects)) + " of " + str(numTotalObjects) + " objects are publicly readable.")
            url = "https://" + result["bucket"] + "." + result["region"] + ".amazonaws.com/"
            for object in readableObjects:
                toWrite.append("    " + url + str(object))

    file.write("\n".join(toWrite))
    file.close()
    #puts(colored.white("Object read results written to " + filepath))

def writeReadObjectAclsResult(path, results):
    filepath = os.path.join(path, "read-objects-acl-results.txt")
    file = open(filepath, "w")

    toWrite = []
    for result in results:
        if result["region"] is None or result["objectACLs"] is None:
            continue

        if result["objectACLs"]["testresult"] == "pass":
            toWrite.append("s3://" + result["bucket"] + " : Permission denied for reading all object ACLs.")
        else:
            readableObjectACLs = result["objectACLs"]["testdata"]
            numTotalObjects = len(result["objects"]["testdata"])
            toWrite.append("s3://" + result["bucket"] + " : " + str(len(readableObjectACLs)) + " of " + str(numTotalObjects) + " objects have publicly readable ACLs.")
            url = "https://" + result["bucket"] + "." + result["region"] + ".amazonaws.com/"
            for object, grants in readableObjectACLs:
                toWrite.append("    " + url + str(object))
                toWrite.append("        grants: " + str(grants))

    file.write("\n".join(toWrite))
    file.close()
    #puts(colored.white("Object ACL read results written to " + filepath))

def writeWriteObjectResult(path, results):
    filepath = os.path.join(path, "write-object-results.txt")
    file = open(filepath, "w")

    toWrite = []
    for result in results:
        if result["region"] is None or result["writeResults"] is None:
            continue

        if result["writeResults"]["testresult"] == "pass":
            toWrite.append("s3://" + result["bucket"] + " : Permission denied for writing an object to the bucket.")
        else:
            writtenObject = result["writeResults"]["testdata"]

            toWrite.append("s3://" + result["bucket"] + " : Successfully wrote an object to the bucket.")
            toWrite.append("    " + writtenObject)

    file.write("\n".join(toWrite))
    file.close()
    #puts(colored.white("Object write results written to " + filepath))

def writeSummary(path, results):
    summaryfile = os.path.join(path, "summary.txt")

    headers = [
        "Bucket Name",
        "Bucket URI",
        "Read Bucket Index",
        "Read Bucket ACL",
        "Read Objects",
        "Read Object ACLs",
        "Write to Bucket"
    ]

    data = []
    for result in results:
        bucketname = result["bucket"]

        readIndex,readAcl,readObjects,readObjectACLs,writeToBucket = ("Not Tested","Not Tested","Not Tested","Not Tested","Not Tested")

        if result["region"] is None:
            bucketuri = "Not a bucket"
        else:
            bucketuri = bucketname+"."+result["region"]+".amazonaws.com"

        if result["objects"] is not None:
            if result["objects"]["testresult"] == "pass":
                readIndex = "PASS"
            else:
                readIndex = "FAIL"

        if result["bucketacl"] is not None:
            if result["bucketacl"]["testresult"] == "pass":
                readAcl = "PASS"
            else:
                readAcl = "FAIL"

        if result["readableObjects"] is not None:
            if result["readableObjects"]["testresult"] == "pass":
                readObjects = "PASS"
            else:
                readObjects = "FAIL"

        if result["objectACLs"] is not None:
            if result["objectACLs"]["testresult"] == "pass":
                readObjectACLs = "PASS"
            else:
                readObjectACLs = "FAIL"

        if result["writeResults"] is not None:
            if result["writeResults"]["testresult"] == "pass":
                writeToBucket = "PASS"
            else:
                writeToBucket = "FAIL"

        row = [bucketname, bucketuri, readIndex, readAcl, readObjects, readObjectACLs, writeToBucket]
        data.append(row)

    str = tabulate.tabulate(data, headers=headers, tablefmt="orgtbl")

    f = open(summaryfile, "w")
    f.write(str)
    f.close()
    #puts(colored.white("Summary written to " + summaryfile))


def writeFilesearchResults(path, results):
    filepath = os.path.join(path, "filename-search-results.txt")
    file = open(filepath, "w")

    toWrite = []
    for result in results:
        if result["region"] is None or result["fileSearchResults"] is None:
            continue

        if result["fileSearchResults"]["testresult"] == "pass":
            toWrite.append("s3://" + result["bucket"] + " : None of the filenames in the bucket matched any of our filters.")
        else:

            pathlist = result["fileSearchResults"]["testdata"]

            toWrite.append("s3://" + result["bucket"] + " : " + str(len(pathlist)) + " objects matched at least one filename filter.")

            allfilters = []
            for (_,filters) in pathlist:
                allfilters = allfilters + filters

            uniquefilters = list(set(allfilters))

            toWrite.append("    Filters Matched: ")
            for filter in uniquefilters:
                count = allfilters.count(filter)
                toWrite.append("        " + str(filter) + " - " + str(count) + " matches")




            for(url,filters) in pathlist:
                toWrite.append("    " + str(filters) + " matched against:")
                toWrite.append("        " + url)

    file.write("\n".join(toWrite))
    file.close()
    #puts(colored.white("Object ACL read results written to " + filepath))


def writeResults(origtarget, results, invasive, filesearch, objects):
    valid_filename_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    file = ''.join(c for c in origtarget if c in valid_filename_chars) + "-result"
    path = os.path.join(os.getcwd(), file)
    puts(colored.white("Results will be saved to " + path + "/*"))
    try:
        os.mkdir(path)
    except OSError:
        puts(colored.yellow("Deleting previous test results."))
        shutil.rmtree(path)
        os.mkdir(path)
        pass


    writeSummary(path, results)
    writeIndexReadResults(path, results)
    buildtree(path, results)
    writeReadAclResults(path,results)
    if objects:
        writeReadObjectsResult(path, results)
        writeReadObjectAclsResult(path, results)
    if invasive:
        writeWriteObjectResult(path, results)
    if filesearch:
        writeFilesearchResults(path, results)
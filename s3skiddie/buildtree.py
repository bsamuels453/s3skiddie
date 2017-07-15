import os, stat


#screw you guido i'll recursion all i want
def addItem(url, partsRemaining, dict):
    if partsRemaining == []:
        return dict

    if len(partsRemaining) != 0:
        if partsRemaining[0] == "":
            #url = "n/a"
            #partsRemaining[0] = "s3skiddie_this_folder_is_intentionally_empty"
            return dict
    else:
        print("weird: " + str(url) + " " )
        return dict



    if type(dict) == str:
        #this only happens when their bucket is fucky and has directories with the same names as files.
        #just disregard the file, screw it
        dict = {}

    if len(partsRemaining) == 1:
        # we're at the end of the tree, this is a file
        dict[partsRemaining[0]] = url + partsRemaining[0] + "  "
        return dict
    else:
        #not at the end of the tree, part0 is a directory
        part0 = partsRemaining[0]

        if part0 not in dict:
            newdict = {}
            if type(newdict) is not type({}):
                print("11returning non dict " + "   " + str(newdict))

            newdict = addItem(url + part0 + "/", partsRemaining[1:], newdict)
            dict[part0] = newdict

            return dict
        else:
            if type(dict) is not type({}):
                print("returning non dict " + "   " + str(dict))

            newdict = addItem(url + part0 + "/", partsRemaining[1:], dict[part0])
            dict[part0] = newdict

            return dict


def buildTreeDatastructure(url, items):
    split = []
    for item in items:
        split.append(item.split("/"))
    ret = {}
    for item in split:
        ret = addItem(url, item, ret)
    return ret


#more recursion, come @ me
def buildTreeOnFilesystem(bucketname,basepath, treepath, tree):
    for k,v in tree.items():
        if type(v) is not dict:
            #it's a file not a directory
            filepath = os.path.join(os.path.join(basepath,treepath), k)
            f = open(filepath, "w")
            f.write(v)
            f.close()
        else:
            #it's a directory. this os.path.join business is a bit confusing, todo:cleanup
            dirpath = os.path.join(os.path.join(basepath,treepath), k)
            os.mkdir(dirpath)
            fname = "s3skiddie_syncdir"
            fcontents = """#!/bin/sh
aws s3 sync s3://""" + bucketname + "/"+ os.path.join(treepath,k) + """ .
echo "Bucket synced to current working directory"
"""

            fpath = os.path.join(dirpath, fname)
            f = open(fpath, "w")
            f.write(fcontents)
            f.close()
            st = os.stat(fpath)
            os.chmod(fpath, st.st_mode | stat.S_IEXEC)
            buildTreeOnFilesystem(bucketname,basepath, os.path.join(treepath,k),v)


def buildtree(path, results):
    for result in results:
        if result["region"] is None or result["objects"] is None:
            continue

        if result["objects"]["testresult"] != "pass":
            url = "https://" + result["bucket"] + "." + result["region"] + ".amazonaws.com/"
            tree = buildTreeDatastructure(url, result["objects"]["testdata"])
            basepath = os.path.join(path, result["bucket"] + "-tree")
            os.mkdir(basepath)

            buildTreeOnFilesystem(result["bucket"],basepath, "",tree)


       #
            #toWrite.append("s3://" + result["bucket"] + "  :  Index permission denied.")
       # else:
           # objects = result["objects"]["testdata"]
            #toWrite.append("s3://" + result["bucket"] + "  :  " + str(len(objects)) + " objects found in index.")
            #for object in objects:
            #    toWrite.append("    " + url + object)

    #file.write("\n".join(toWrite))
    #file.close()

    #filepath = os.path.join(path, "index-read-results.txt")
    #file = open(filepath, "w")

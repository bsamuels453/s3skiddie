import boto
import argparse
import s3skiddie.unauthenticated as unauth
from clint.textui import puts, colored, indent, progress
import sys, os, binascii
from functools import partial
from multiprocessing import Process, Value, Array, Pool, Queue, Manager
import time
from ctypes import c_int
import re
import pkg_resources

def getBucketRegion(bucket):
    puts(colored.white('Figuring out region for '+ str(bucket)) )
    region = unauth.getBucketRegion(bucket)
    with indent(4, quote='   '):
        if region is None:
            puts(colored.red('AWS returned BucketDoesNotExist.'))
            return None
        else:
            if region[:2] != "s3":
                region = "s3-" + region
            puts(colored.green('Bucket resides at ' + region))
    return region

def testPublicListBucket(idx, bucket, region):
    puts(colored.white('[Test '+idx+'] Checking bucket list permission (public)'))
    with indent(4, quote='   '):
        bucketObjects = unauth.listBucketContents(bucket, region)
        if bucketObjects is None:
            puts(colored.green('Permission denied for public bucket listing'))
            return {"testresult":"pass", "testdata":None}
        else:
            url = "https://"+region+".amazonaws.com/"+bucket+"/"
            puts(colored.yellow('Public users can list objects in this bucket'))
            puts(colored.yellow(str(len(bucketObjects))+ " objects found in bucket."))
            puts(colored.yellow("Nav here to see the full index: " + url))
            return {"testresult": "fail", "testdata": bucketObjects}

def testPublicReadBucketACL(idx,bucket, region):
    puts(colored.white('[Test '+idx+'] Checking bucket ACL read permission (public)'))
    with indent(4, quote='   '):
        bucketACL = unauth.getBucketACL(bucket, region)
        if bucketACL is None:
            puts(colored.green('Permission denied for reading public bucket ACL'))
            return {"testresult": "pass", "testdata": None}
        else:
            url = "https://" + region + ".amazonaws.com/" + bucket + "/?acl"
            puts(colored.red("Public users may read this bucket's ACL"))
            puts(colored.red(str(len(bucketACL)) + " ACL grants found attached to this bucket"))
            puts(colored.red("Nav here to see the ACL: " + url))
            return {"testresult": "fail", "testdata": bucketACL}

def parallelGetObjectRequest(bucket, region, object):
    objData = unauth.getObject(bucket, region, object)
    if objData is not None:
        return (object,len(objData))
    return None



def testPublicReadObject(idx,bucket, region, bucketObjects, objectScan):
    if not objectScan:
        puts(colored.white('[Test '+idx+'] Skipping public object read test. Use --objects to enable.'))
        return None

    if bucketObjects is not None:
        puts(colored.white('[Test '+idx+'] Testing public read permission of the ' + str(len(bucketObjects)) + " objects that were in the bucket index."))

        with indent(4, quote='   '):
            pool = Pool(processes=50)
            f = partial(parallelGetObjectRequest, bucket, region)
            result_async = pool.map_async(f, bucketObjects)
            pool.close()
            pool.join()
            result_async.wait()
            results = result_async.get()

            numReadableObjects = 0
            for result in results:
                if result is not None:
                    numReadableObjects += 1

            if numReadableObjects is 0:
                puts(colored.green('Permission denied for publicly reading all ' + str(len(bucketObjects)) + " objects in bucket."))
                return {"testresult": "pass", "testdata": None}
            else:
                puts(colored.yellow(
                    str(numReadableObjects) +" out of "+ str(len(bucketObjects)) + " objects in the bucket are publicly readable."))
                return {"testresult": "fail", "testdata": results}
    else:
        puts(colored.yellow(
            '[Test '+idx+'] Skipping public object read test since we cannot obtain a list of objects to test against.'))
        return None

def parallelGetObjectACLRequest(bucket, region,object):
    grants = unauth.getObjectACL(bucket, region, object)
    if grants is not None:
        return (object, grants)
    return None


def testPublicReadObjectACL(idx,bucket, region, bucketObjects, objectScan):
    if not objectScan:
        puts(colored.white('[Test '+idx+'] Skipping public object read ACL test. Use --objects to enable.'))
        return None


    if bucketObjects is not None:
        puts(colored.white('[Test '+idx+'] Testing public ACL read permission of the ' + str(len(bucketObjects)) + " objects that were in the bucket index."))

        with indent(4, quote='   '):

            pool = Pool(processes=50)
            f = partial(parallelGetObjectACLRequest, bucket, region)
            result_async = pool.map_async(f, bucketObjects)
            pool.close()
            pool.join()
            result_async.wait()
            results = result_async.get()

            pubGrants = []
            for result in results:
                if result is not None:
                    pubGrants.append(result)



            if (len(pubGrants)) is 0:
                puts(colored.green('Permission denied for publicly reading all ' + str(len(bucketObjects)) + " object ACLs in bucket."))
                return {"testresult": "pass", "testdata": None}
            else:
                puts(colored.red(
                    str(len(pubGrants)) +" out of "+ str(len(bucketObjects)) + " objects in the bucket have publicly readable ACLs."))
                #for k in objectACLs.keys():
                #    url = "https://" + region + ".amazonaws.com/" + bucket + "/" + k + "?acl"
                #    puts(colored.red("ACL for " + k + " can be viewed at " + url))
                return {"testresult": "fail", "testdata": pubGrants}
    else:
        puts(colored.yellow(
            '[Test '+idx+'] Skipping public object ACL read test since we cannot obtain a list of objects to test against.'))
        return None
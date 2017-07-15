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

def testPublicObjectWrite(idx, bucket, region, invasive):
    if not invasive:
        puts(colored.white('[Test '+idx+'] Skipping public object write test. Use --invasive to enable.'))
        return None
    puts(colored.white('[Test '+idx+'] Attempting to write an object to the bucket without authentication.'))

    with indent(4, quote='   '):
        filename = binascii.b2a_hex(os.urandom(16)).decode("ASCII")+".html"
        filecontent = "WARNING: THIS BUCKET HAS PUBLIC WRITE PERMISSIONS"
        res = unauth.writeTestObject(bucket, region, filename, filecontent)

        if res is not None:
            url = "https://" + region + ".amazonaws.com/" + bucket + "/" + filename
            puts(colored.red('Successfully wrote a test object to the bucket without any authentication.'))
            puts(colored.red('See object at ' + url))
            return {"testresult": "fail", "testdata": url}
        else:
            puts(colored.green('Failed to write test object to the bucket.'))
            return {"testresult": "pass", "testdata": None}



def testPublicAclWrite(idx, bucket, region):
    puts(colored.white('[Test '+idx+'] Attempting ACL write to bucket (public)'))

    with indent(4, quote='   '):
        cannedAcl = "public-read"
        res = unauth.writeBucketAcl(bucket,region,cannedAcl)

        if res is not None:
            puts(colored.red("Successfully wrote to the bucket's ACL without authentication. 'public-read' ACL applied to bucket."))
        else:
            puts(colored.green("Failed to write to the bucket's ACL"))


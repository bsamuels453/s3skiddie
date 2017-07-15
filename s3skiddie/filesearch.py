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


def fileSearchTest(idx, bucket, region, objects, filesearch):
    if not filesearch:
        puts(colored.white("[Test " + idx + "] Skipping file search test. Use --filesearch to enable."))
        return None
    if objects is None:
        puts(colored.yellow("[Test " + idx + "] Skipping sensitive file search test because we cannot obtain a list of objects to test against."))
        return None


    searchList = pkg_resources.resource_string(__name__, "sensitiveFiles.txt")
    searchItems = searchList.decode("UTF-8").splitlines()

    puts(colored.white("[Test " + idx + '] Checking ' + str(len(objects)) + " bucket objects for potentially sensitive files"))
    numObjectMatches = 0
    numFilterMatches = 0

    ret = []

    with indent(4, quote='   '):
        for obj in objects:
            #lastpart = obj.split("/")[-1]
            res = []
            lower = obj.lower()
            for item in searchItems:
                if item in lower:
                    numFilterMatches += 1
                    res.append(item)
            if len(res) != 0:
                numObjectMatches += 1
                url = "https://" + region + ".amazonaws.com/" + bucket + "/" + obj
                ret.append((url,res))
        if numObjectMatches != 0:
            puts(colored.yellow("In total, " + str(numObjectMatches) + " objects matched against " + str(numFilterMatches) + " filters."))
            return {"testresult": "fail", "testdata": ret}
        else:
            puts(colored.green("No bucket objects matched against any filters"))
            return {"testresult": "pass", "testdata": None}

import argparse
from clint.textui import puts, colored, indent, progress
import pkg_resources, sys, os.path, string
import s3skiddie.filesearch as filesearch
import s3skiddie.unauth_noninvasive as unauth_noninvasive
import s3skiddie.unauth_invasive as unauth_invasive
import s3skiddie.output as output


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parseArgs():
    wordlist = pkg_resources.resource_filename(__name__, "sensitiveFiles.txt")
    parser = Parser(prog="s3skiddie", description="""Perform a blackbox security audit of Amazon S3 bucket permissions and content. Do not use this tool without the permission of the bucket owner.""")
    parser.add_argument("-i", "--invasive", help="Use this to enable invasive tests such as testing object write permissions.",const=True, default=False, action="store_const")
    parser.add_argument("-f", "--filesearch", help="Use this to search the bucket for sensitive file names. Search is conducted by checking object names and paths for key phrases that indicate that it might contain sensitive information. Wordlist located at " + wordlist,const=True, default=False, action="store_const")
    parser.add_argument("-o", "--objects", help="Check the permissions for individual objects inside the bucket. Bandwidth intensive and may take a very long time to run.", const=True, default=False, action="store_const")

    parser.add_argument("--file", help="Analyze a list of buckets from a file.", action='store_true', default=False)

    parser.add_argument("target", help="The name of the bucket to be analyzed; or if using --file, the file containing buckets to be analyzed.", type=str)

    args = parser.parse_args()
    return args

def scanBucket(bucket, invasive, fileSearch, objectScan):
    puts(colored.white('Scan Target: ') + colored.green('s3://' + bucket))
    with indent(4, quote=colored.cyan(' |')):
        bucketObjects,bucketACL,readableObjects,objectACLs,writeResults,fileSearchResults=(None,None,None,None,None,None)
        region = unauth_noninvasive.getBucketRegion(bucket)
        if region is not None:
            idx = 1

            bucketObjects = unauth_noninvasive.testPublicListBucket(str(idx), bucket, region)
            idx +=1
            bucketACL = unauth_noninvasive.testPublicReadBucketACL(str(idx), bucket, region)
            idx += 1
            readableObjects = unauth_noninvasive.testPublicReadObject(str(idx), bucket, region, bucketObjects["testdata"], objectScan)
            idx += 1
            objectACLs = unauth_noninvasive.testPublicReadObjectACL(str(idx), bucket, region, bucketObjects["testdata"], objectScan)
            idx += 1
            writeResults = unauth_invasive.testPublicObjectWrite(str(idx), bucket, region, invasive)
            idx += 1
            fileSearchResults = filesearch.fileSearchTest(str(idx), bucket, region, bucketObjects["testdata"], fileSearch)


    puts(colored.white('Finished scanning bucket s3://' + bucket))
    return {
        "bucket":bucket,
        "region":region,
        "objects":bucketObjects,
        "bucketacl":bucketACL,
        "readableObjects":readableObjects,
        "objectACLs":objectACLs,
        "writeResults":writeResults,
        "fileSearchResults":fileSearchResults
    }


def execute(argv):
    args = parseArgs()
    target = args.target

    puts(colored.white('Starting s3skiddie'))
    if  args.invasive:
        puts(colored.white('Invasive Scan: ') + colored.red('ENABLED'))
    else:
        puts(colored.white('Invasive Scan: ') + colored.green('Disabled'))
    if args.filesearch:
        puts(colored.white('File Search: ') + colored.red('ENABLED'))
    else:
        puts(colored.white('File Search: ') + colored.green('Disabled'))
    if args.objects:
        puts(colored.white('Object Scan: ') + colored.red('ENABLED'))
    else:
        puts(colored.white('Object Scan: ') + colored.green('Disabled'))


    if args.file:
        try:
            f = open(target,"r")
            bucketlist = f.readlines()
            f.close()
            bucketlist = [x.strip() for x in bucketlist]
            puts(colored.cyan(str(len(bucketlist)) + " potential buckets loaded from file for testing."))
        except Exception as e:
            puts(colored.red("Could not open target file, " + str(e)))
            sys.exit(1)
    else:
        if target[:5] == "s3://":
            target = target[4:]
        bucketlist = [target]

    results = []
    for bucket in bucketlist:
        result = scanBucket(bucket, args.invasive, args.filesearch, args.objects)
        results.append(result)

    output.writeResults(target, results, args.invasive, args.filesearch, args.objects)
    puts(colored.white("All done!"))








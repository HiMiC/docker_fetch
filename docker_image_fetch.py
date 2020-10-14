import os
import json
import optparse
import requests
import time
import os
from datetime import datetime

# pulls Docker Images from unauthenticated docker registry api. 
# and checks for docker misconfigurations. 

apiversion = "v2"
final_list_of_blobs = []

# Disable insecure request warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = optparse.OptionParser()
parser.add_option('-u', '--url', action="store", dest="url",
                  help="URL Endpoint for Docker Registry API v2. Eg https://IP:Port",
                  default="none")
options, args = parser.parse_args()
url = options.url


def list_repos():
    req = requests.get(url + "/" + apiversion + "/_catalog", verify=False)
    return json.loads(req.text)["repositories"]


def find_tags(reponame):
    print "SLEEP 10 TAG"
    time.sleep(10)
    req = requests.get(url + "/" + apiversion + "/" + reponame + "/tags/list", verify=False)
    filename = "tags.json"
    with open(reponame + "/" + filename, 'wb') as test:
        test.write(req.content)
    print "\n"
    data = json.loads(req.content)
    if "tags" in data:
        return data["tags"]


def list_blobs(reponame, tag):
    print "SLEEP 10 BLOBS"
    time.sleep(10)
    req = requests.get(url + "/" + apiversion + "/" + reponame + "/manifests/" + tag, verify=False)
    filename = "manifests.json"
    with open(reponame + "/" + tag + "/" + filename, 'wb') as test:
        test.write(req.content)
    data = json.loads(req.content)
    if "fsLayers" in data:
        for x in data["fsLayers"]:
            curr_blob = x['blobSum'].split(":")[1]
            if curr_blob not in final_list_of_blobs:
                final_list_of_blobs.append(curr_blob)


def download_blobs(reponame, blobdigest, dirname):
    req = requests.get(url + "/" + apiversion + "/" + reponame + "/blobs/sha256:" + blobdigest, verify=False)
    filename = "%s.tar.gz" % blobdigest
    with open(dirname + "/" + filename, 'wb') as test:
        test.write(req.content)


def main():
    if url is not "spam":
        list_of_repos = list_repos()
        print "\n[+] List of Repositories:\n"
        for x in list_of_repos:
            print x
            if os.path.isdir(x):
                print (x + " exist")
            else:
                os.makedirs(x)

            # target_repo = raw_input("\nWhich repo would you like to download?:  ")
            target_repo = x

            print target_repo + '/success.txt'
            if not os.path.isfile(target_repo + '/success.txt'):
                print "SLEEP 10 sec repo " + target_repo
                time.sleep(10)
                if target_repo in list_of_repos:
                    tags = find_tags(target_repo)
                    if tags is not None:
                        print "\n[+] Available Tags:\n"
                        for x2 in tags:
                            print x2
                            if os.path.isdir(target_repo + '/' + x2):
                                print (target_repo + '/' + x2 + " exist")
                            else:
                                os.makedirs(target_repo + '/' + x2)

                            # target_tag = raw_input("\nWhich tag would you like to download?:  ")
                            target_tag = x2
                            if target_tag in tags:
                                dirname = target_repo + '/' + x2
                                if os.path.isdir(dirname):
                                    print (dirname + " exist")
                                else:
                                    os.makedirs(dirname)
                                print dirname + '/success.txt'
                                if not os.path.isfile(dirname + '/success.txt'):
                                    list_blobs(target_repo, target_tag)
                                    # dirname = raw_input("\nGive a directory name:  ")
                                    # os.makedirs(dirname)

                                    print "Now sit back and relax. I will download all the blobs for you in %s directory. \nOpen the directory, unzip all the files and explore like a Boss. " % dirname
                                    for x3 in final_list_of_blobs:
                                        print "\n[+] Downloading Blob: %s" % x3
                                        download_blobs(target_repo, x3, dirname)

                                    now = datetime.now()
                                    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                                    print dirname + '/success.txt'
                                    with open(dirname + '/success.txt', 'w') as test:
                                        test.write(date_time)
                                    print "SLEEP 10 sec" + date_time
                                    time.sleep(10)
                                else:
                                    print ("SUCCESS PROPUSK " + dirname)
                                    print "SLEEP 10 sec"
                                    time.sleep(10)
                            else:
                                print "No such Tag Available. Qutting...."
                    else:
                        print "[+] No Tags Available. Quitting...."

                else:
                    print "1No such repo found. Quitting...."
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                print target_repo + '/success.txt'
                with open(target_repo + '/success.txt', 'w') as test:
                    test.write(date_time)
                print "SLEEP 10 sec" + date_time
                time.sleep(10)
            else:
                print "2No such repo found. Quitting...."
    else:
        print "\n[-] Please use -u option to define API Endpoint, e.g. https://IP:Port\n"


if __name__ == "__main__":
    main()

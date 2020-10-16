#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import json
import optparse
import requests
import time
import os
from datetime import datetime
from urlparse import urlparse
import sys
from termcolor import colored, cprint

# pulls Docker Images from unauthenticated docker registry api.
# and checks for docker misconfigurations.

apiversion = "v2"
final_list_of_blobs = []

DEBUG = 1
SLEEP_TIME = 3

# Disable insecure request warning
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

parser = optparse.OptionParser()
parser.add_option('-u', '--url', action="store", dest="url",
                  help="URL Endpoint for Docker Registry API v2. Eg https://IP:Port",
                  default="spam")
options, args = parser.parse_args()
url = options.url


def list_repos(save_path):
    url2 = url + "/" + apiversion + "/_catalog"
    # cprint('GET: '+url2, 'green', 'on_red')
    cprint('GET: ' + url2, 'green')
    req = requests.get(url2, verify=False)
    with open(save_path + '/_catalog', 'w') as test:
        test.write(req.text)
    return json.loads(req.text)["repositories"]


def find_tags(target_repo,reponame):

    url2 = url + "/" + apiversion + "/" + reponame + "/tags/list"
    colored("GET:" + url2, 'blue')
    if DEBUG:
        print "SLEEP ",SLEEP_TIME," TAG"
        time.sleep(SLEEP_TIME)
    req = requests.get(url2, verify=False)
    filename = target_repo + "/" + "tags.json"
    colored("SAVE:" + filename, 'blue')
    with open(filename, 'wb') as test:
        test.write(req.content)
    print "\n"
    data = json.loads(req.content)
    if "tags" in data:
        return data["tags"]


def list_blobs(target_repo,reponame, tag):
    print "SLEEP ",SLEEP_TIME," BLOBS"
    if DEBUG:
        time.sleep(SLEEP_TIME)
    url2 = url + "/" + apiversion + "/" + reponame + "/manifests/" + tag
    print url2
    req = requests.get(url2, verify=False)
    filename = "manifests.json"
    with open(target_repo+ "/" + tag + "/" + filename, 'wb') as test:
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
        o = urlparse(url)
        host_name = o.netloc
        print host_name
        save_path = host_name + "/docker/"
        cprint('save_path: ' + save_path, 'green')
        if os.path.isdir(save_path):
            print (save_path + " exist")
        else:
            os.makedirs(save_path)

        list_of_repos = list_repos(save_path)
        print list_of_repos
        # exit()
        print "\n[+] List of Repositories:\n"

        for x in list_of_repos:
            target_repo = save_path + x

            cprint('target_repo: ' + target_repo, 'green')
            if os.path.isdir(target_repo):
                print (target_repo + " exist")
            else:
                os.makedirs(target_repo)

            print target_repo + '/success.txt'
            if not os.path.isfile(target_repo + '/success.txt'):
                print "SLEEP ",SLEEP_TIME," sec repo " + target_repo
                if DEBUG:
                    time.sleep(SLEEP_TIME)
                if x in list_of_repos:

                    cprint("111 target_repo: " + target_repo, 'red')
                    tags = find_tags(target_repo,x)

                    # print target_repo
                    # print x
                    # print tags
                    if tags is not None:
                        print "\n[+] Available Tags:\n"
                        for x2 in tags:
                            print x2
                            target_repo_x2 = target_repo + '/' + x2
                            cprint('target_repo_x2:' + target_repo_x2, 'green')
                            if os.path.isdir(target_repo_x2):
                                print (target_repo_x2 + " exist")
                            else:
                                os.makedirs(target_repo_x2)

                            # target_tag = raw_input("\nWhich tag would you like to download?:  ")
                            target_tag = x2
                            if target_tag in tags:
                                dirname = target_repo + '/' + target_tag
                                cprint("dirname: " + dirname, 'red', 'on_green')
                                if os.path.isdir(dirname):
                                    print (dirname + " exist")
                                else:

                                    os.makedirs(dirname)
                                print dirname + '/success.txt'
                                if not os.path.isfile(dirname + '/success.txt'):
                                    print target_tag
                                    list_blobs(target_repo,x, target_tag)
                                    # list_blobs(target_repo, target_tag)
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
                                    print "SLEEP ",SLEEP_TIME," sec" + date_time
                                    if DEBUG:
                                        time.sleep(SLEEP_TIME)
                                else:
                                    print ("SUCCESS PROPUSK " + dirname)
                                    print "SLEEP ",SLEEP_TIME," sec"
                                    if DEBUG:
                                        time.sleep(SLEEP_TIME)
                            else:
                                cprint("No such Tag Available. Qutting....", 'blue', 'on_red')
                    else:
                        cprint("[+] No Tags Available. Quitting....",'blue','on_red')

                else:
                    cprint("1No such repo found. Quitting....", 'blue', 'on_red')
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                print target_repo + '/success.txt'
                with open(target_repo + '/success.txt', 'w') as test:
                    test.write(date_time)
                print "SLEEP ", SLEEP_TIME," sec" + date_time
                if DEBUG:
                    time.sleep(SLEEP_TIME)
                cprint("3333  such repo LIST_OF_REPO", 'blue', 'on_red')
            else:
                print ""
                cprint("\n 2222 No such REPO found. Quitting....", 'blue', 'on_red')
    else:
        print ""
        cprint("\n 1111 [-] Please use -u option to define API Endpoint, e.g. https://IP:Port\n", 'blue', 'on_red')


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
import os
import json
import optparse
import requests
import time
import os
from datetime import datetime
from urlparse import urlparse

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
                  default="spam")
options, args = parser.parse_args()
url = options.url


def list_repos():
    req = requests.get(url, verify=False)
    return json.loads(req.text)


def find_tags(url, reponame):
    # print "SLEEP 10 TAG"
    # time.sleep(10)
    o3 = urlparse(url)
    host_name = o3.scheme + "://" + o3.netloc
    url2 = host_name + "/service/rest/v1/components?repository=" + reponame
    print "get: " + url2
    req = requests.get(url2, verify=False)
    filename = "tags.json"
    with open(o3.netloc + "/repository/" + reponame + "/" + filename, 'wb') as test:
        test.write(req.content)
    print "\n"
    data = json.loads(req.content)
    # return data
    if "items" in data:
        return data["items"]


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


# def download_blobs(reponame, blobdigest, dirname):
#     req = requests.get(url + "/" + apiversion + "/" + reponame + "/blobs/sha256:" + blobdigest, verify=False)
#     filename = "%s.tar.gz" % blobdigest
#     with open(dirname + "/" + filename, 'wb') as test:
#         test.write(req.content)

def download_blobs(dirname, filename, downloadUrl):
    print "dirname: " + dirname
    print "filename: " + filename
    print "get file: " + downloadUrl
    req = requests.get(downloadUrl, verify=False)
    # filename = "%s.tar.gz" % blobdigest
    with open(dirname + "/" + filename, 'wb') as test:
        test.write(req.content)


def main():
    if url is not "spam":
        list_of_repos = list_repos()
        print "\n[+] List of Repositories:\n"

        o = urlparse(url)
        host_name = o.netloc
        print o.netloc
        if os.path.isdir(host_name):
            print (host_name + " exist")
        else:
            os.makedirs(host_name)

        for x in list_of_repos:
            o2 = urlparse(x['url'])
            path_repo = o2.netloc + o2.path
            print "path_repo: " + path_repo
            if os.path.isdir(path_repo):
                print (path_repo + " exist")
            else:
                os.makedirs(path_repo)

            print path_repo + '/success.txt'
            # exit()
            if not os.path.isfile(path_repo + '/success.txt'):
                tags = find_tags(url, x['name'])
                if tags is not None:
                    print "\n[+] Available Tags:\n"
                    for x2 in tags:
                        # print x2
                        for x3 in x2['assets']:
                            print x3['path']

                            dir_path = os.path.dirname(os.path.realpath("/"+x3['path']))
                            print "dir_path: " +dir_path

                            path_dir_save = path_repo+dir_path
                            print "path_dir_save: " + path_dir_save
                            if os.path.isdir(path_dir_save):
                                print (path_dir_save + " exist")
                            else:
                                os.makedirs(path_dir_save)
                            file_save_path = x3['path']

                            if x3['format'] == "nuget":
                                file_save_path = x3['path']+".nupkg"

                            download_blobs(path_repo,file_save_path,x3['downloadUrl'])
                            print "SLEEP 3 sec"
                            time.sleep(3)


                        # exit()
                        # if os.path.isdir(target_repo + '/' + x2):
                        #     print (target_repo + '/' + x2 + " exist")
                        # else:
                        #     os.makedirs(target_repo + '/' + x2)
                    now = datetime.now()
                    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                    with open(path_repo + '/success.txt', 'w') as test:
                      test.write(date_time)
                    print "SLEEP 10 sec" + date_time
                    time.sleep(10)
                else:
                    print "2No such repo found. Quitting...."
            else:
                print "SLEEP 3"
                time.sleep(3)

    else:
        print "\n[-] Please use -u option to define API Endpoint, e.g. https://IP:Port\n"


if __name__ == "__main__":
    main()

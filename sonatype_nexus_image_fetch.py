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

DEBUG = 0
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


def list_repos():
    req = requests.get(url, verify=False)
    return json.loads(req.text)


def create_path(path):
    if os.path.isdir(path):
        print (path + " exist")
    else:
        os.makedirs(path)


def geturl(url2, token=None):
    # data_all_items = list()
    data_all_items = []

    if token:
        url3 = url2 + "&continuationToken=" + token
        print "get url3: " + url3
        req = requests.get(url3, verify=False)
        data = json.loads(req.content)
    else:
        print "get url2: " + url2
        req = requests.get(url2, verify=False)
        data = json.loads(req.content)

    print "len: ", len(data['items'])

    print "continuationToken: ", data['continuationToken']
    if "items" in data:
        data_all_items = data["items"]

        if data['continuationToken'] is not None:
            # print "SLEEP ",SLEEP_TIME
            # time.sleep(SLEEP_TIME)
            data2 = geturl(url2, data['continuationToken'])

            if len(data2):
                data_all_items.extend(data2)
    print "\r\n"
    return data_all_items


def find_tags(url, reponame):
    # print "SLEEP ",SLEEP_TIME," TAG"
    # time.sleep(SLEEP_TIME)
    o3 = urlparse(url)
    host_name = o3.scheme + "://" + o3.netloc
    url2 = host_name + "/service/rest/v1/components?repository=" + reponame
    # url2 = host_name + "/service/rest/v1/search?repository=" + reponame + "&name=*"
    print "get: " + url2

    data = geturl(url2)
    print ("-=-=-=-=-")
    print type(data)
    print len(data)
    print ("-=-=-=-=-")
    filename = "tags.json"
    with open(o3.netloc + "/repository/" + reponame + "/" + filename, 'wb') as test:
        # test.write(req.content)
        test.write(json.dumps(data, indent=4))
    print "\n"
    # data = json.loads(req.content)
    # return data
    # if "items" in data:
    #     return data["items"]
    return data


def list_blobs(reponame, tag):
    if DEBUG:
        print "SLEEP ", SLEEP_TIME, " BLOBS"
        time.sleep(SLEEP_TIME)

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

        # создаем папку если нет
        create_path(host_name)

        for x in list_of_repos:
            o2 = urlparse(x['url'])
            path_repo = o2.netloc + o2.path
            print "path_repo: " + path_repo

            # создаем папку если нет
            create_path(path_repo)

            print path_repo + '/success.txt'
            # exit()
            if not os.path.isfile(path_repo + '/success.txt'):
                tags = find_tags(url, x['name'])
                tags_count = len(tags)
                print "COUNT TAGS: ", tags_count
                # exit()
                count_download = 0
                if tags is not None:
                    print "\n[+] Available Tags:\n"
                    for x2 in tags:
                        count_download += 1
                        print "скачивается tags: ", count_download, " из ", tags_count, "процентов ", "{0:.0%}".format(
                            float(count_download) / float(tags_count))
                        # print x2
                        for x3 in x2['assets']:
                            print x3['path']

                            dir_path = os.path.dirname(os.path.realpath("/" + x3['path']))
                            print "dir_path: " + dir_path

                            path_dir_save = path_repo + dir_path
                            print "path_dir_save: " + path_dir_save

                            # создаем папку если нет
                            create_path(path_dir_save)

                            file_save_path = x3['path']

                            if x3['format'] == "nuget":
                                # формат открывается в zip
                                file_save_path = x3['path'] + ".nupkg"
                            print u"CHECK проверка file: " + path_repo + "/" + file_save_path + '_success.txt'
                            if not os.path.isfile(path_repo + "/" + file_save_path + '_success.txt'):
                                # скачиваем
                                download_blobs(path_repo, file_save_path, x3['downloadUrl'])
                                # скачалось успешно
                                now = datetime.now()
                                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                                with open(path_repo + "/" + file_save_path + '_success.txt', 'w') as test:
                                    test.write(date_time)
                                if DEBUG:
                                    print "SLEEP ", SLEEP_TIME, " sec"
                                    time.sleep(SLEEP_TIME)
                            else:
                                print u"PROPUSK пропуск: " + path_repo + "/" + file_save_path

                    now = datetime.now()
                    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                    with open(path_repo + '/success.txt', 'w') as test:
                        test.write(date_time)
                    if DEBUG:
                        print "SLEEP ", SLEEP_TIME, " sec" + date_time
                        time.sleep(SLEEP_TIME)
                else:
                    print "Нет репозитория...."
            else:
                if DEBUG:
                    print "SLEEP ", SLEEP_TIME
                    time.sleep(SLEEP_TIME)

    else:
        print u"\n[-] Используйте опцию -u option to define API Endpoint, e.g. https://IP:Port\n"


if __name__ == "__main__":
    main()

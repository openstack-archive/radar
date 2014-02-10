#!/usr/bin/python

import datetime
import os
import urllib


REMOTES = ['gerrit-stream-logger-dfw.stillhq.com',
           'gerrit-stream-logger-ord.stillhq.com',
           'gerrit-stream-logger-syd.stillhq.com']

one_day = datetime.timedelta(days=1)
day = datetime.datetime(2013, 5, 1)

while day < datetime.datetime.now():
    for target in REMOTES:
        url = 'http://%s/output/%d/%d/%d' %(target, day.year, day.month,
                                            day.day)
        path = os.path.join(target, str(day.year), str(day.month))
        filename = os.path.join(path, str(day.day))

        if not os.path.exists(path):
            os.makedirs(path)

        print '%s Fetching %s' % (datetime.datetime.now(), url)
        try:
            remote = urllib.urlopen(url)
            if remote.getcode() != 404:
                remote_size = remote.info().getheaders('Content-Length')[0]
                remote_size = int(remote_size)

                if not os.path.exists(filename):
                    local_size = 0
                else:
                    local_size = os.stat(filename).st_size

                print ('%s Local size %s, remote size %s'
                       %(datetime.datetime.now(), local_size, remote_size))
                if remote_size > local_size:
                    with open(filename, 'w') as f:
                        f.write(remote.read())
                        print '%s ... fetched' % datetime.datetime.now()
            remote.close()

        except:
            pass

    day += one_day

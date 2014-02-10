#!/usr/bin/python

import datetime
import os
import urllib


REMOTES = ['gerrit-stream-logger-dfw.stillhq.com',
           'gerrit-stream-logger-ord.stillhq.com',
           'gerrit-stream-logger-syd.stillhq.com']

one_day = datetime.timedelta(days=1)
day = datetime.datetime(2013, 5, 1)

merged_filename = None
merged_data = {}
merged_data_with_order = []

while day < datetime.datetime.now():
    for target in REMOTES:
        url = 'http://%s/output/%d/%d/%d' %(target, day.year, day.month,
                                            day.day)
        single_path = os.path.join(target, str(day.year), str(day.month))
        single = os.path.join(single_path, str(day.day))
        merged_path = os.path.join('merged', str(day.year), str(day.month))
        merged = os.path.join(merged_path, str(day.day))

        if not os.path.exists(single_path):
            os.makedirs(single_path)
        if not os.path.exists(merged_path):
            os.makedirs(merged_path)

        print '%s Fetching %s' % (datetime.datetime.now(), url)
        remote = urllib.urlopen(url)
        if remote.getcode() != 404:
            remote_size = remote.info().getheaders('Content-Length')[0]
            remote_size = int(remote_size)

            if not os.path.exists(single):
                local_size = 0
            else:
                local_size = os.stat(single).st_size

            print ('%s Local size %s, remote size %s'
                   %(datetime.datetime.now(), local_size, remote_size))
            if remote_size > local_size:
                with open(single, 'w') as f:
                    f.write(remote.read())
                    print '%s ... fetched' % datetime.datetime.now()

                if merged_filename != merged:
                    merged_data = {}
                    merged_data_with_order = []
                    print '%s ... loading merge file' % datetime.datetime.now()

                    if os.path.exists(merged):
                        with open(merged, 'r') as f:
                            for line in f.readlines():
                                merged_data[line] = True
                                merged_data_with_order.append(line)
                    merged_filename = merged

                new_entries = 0
                with open(single, 'r') as f:
                    for entry in f.readlines():
                        if not entry in merged_data:
                            merged_data[entry] = True
                            merged_data_with_order.append(entry)
                            new_entries += 1

                with open(merged, 'w') as f:
                    f.write('\n'.join(merged_data_with_order))
                print ('%s ... merged (%d new entries)'
                       % (datetime.datetime.now(), new_entries))

        remote.close()

    day += one_day

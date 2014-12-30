#!/usr/bin/python

import copy
import datetime
import json
import os
import re
import sys
import urllib


REMOTES = ['gerrit-stream-logger-dfw.stillhq.com',
           'gerrit-stream-logger-ord.stillhq.com',
           'gerrit-stream-logger-syd.stillhq.com']

one_day = datetime.timedelta(days=1)
day = datetime.datetime.now()
day -= datetime.timedelta(days=3)

merged_filename = None
merged_data = {}
merged_data_with_order = []

changed_merge_files = {}

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
                                line = line.rstrip()
                                merged_data[line] = True
                                merged_data_with_order.append(line)
                    merged_filename = merged

                new_entries = 0
                with open(single, 'r') as f:
                    for entry in f.readlines():
                        entry = entry.rstrip()
                        if not entry in merged_data:
                            merged_data[entry] = True
                            merged_data_with_order.append(entry)
                            new_entries += 1

                with open(merged, 'w') as f:
                    f.write('\n'.join(merged_data_with_order))
                changed_merge_files[merged] = True
                print ('%s ... merged (%d new entries)'
                       % (datetime.datetime.now(), new_entries))

        remote.close()

    day += one_day

# Reprocess the last 90 days?
FILENAME_RE = re.compile('^merged/([0-9]+)/([0-9]+)/([0-9]+)$')
if True:
    for dirpath, subdirs, files in os.walk('merged'):
        for filename in files:
            m = FILENAME_RE.match('%s/%s' % (dirpath, filename))
            if m:
                dt = datetime.datetime(int(m.group(1)),
                                       int(m.group(2)),
                                       int(m.group(3)))
                age = datetime.datetime.now() - dt
                if age.days < 90:
                    changed_merge_files[os.path.join(dirpath, filename)] = True

print 'Processing changed merge files'
patches = {}


def ninety_days_of_filenames():
    dt = datetime.datetime.now()
    dt -= datetime.timedelta(days=90)

    while dt < datetime.datetime.now():
        yield 'merged/%s/%s/%s' % (dt.year, dt.month, dt.day)
        dt += datetime.timedelta(days=1)
    yield 'merged/%s/%s/%s' % (dt.year, dt.month, dt.day)


for filename in ninety_days_of_filenames():
    if not filename in changed_merge_files:
        continue

    print '... %s' % filename
    with open(filename, 'r') as f:
        reviews = {}
        reviews_verbose = {}

        for line in f.readlines():
            line = line.rstrip()

            try:
                j = json.loads(line)
            except:
                continue

            try:
                if not 'change' in j:
                    continue

                if not 'patchSet' in j:
                    continue

                number = j['change']['number']
                patchset = j['patchSet']['number']
                project = j['change']['project']

                patch_key = 'patches/%s/%s/%s' % (project, number[:2], number)
                if os.path.exists('%s/%s.json' % (patch_key, number)):
                    with open('%s/%s.json' % (patch_key, patchset)) as f:
                        patches.setdefault(patch_key, {})
                        patches[patch_key][patchset] = json.loads(f.read())
                else:
                    patches.setdefault(patch_key, {})
                    patches[patch_key].setdefault(patchset, {})
                patches[patch_key][patchset].setdefault('reviews', [])

                if j['type'] == 'patchset-created':
                    patches[patch_key][patchset]['created'] = \
                        j['patchSet']['createdOn']
                    patches[patch_key][patchset]['sha'] = \
                        j['patchSet']['revision']

                elif j['type'] == 'comment-added':
                    author = j['author'].get('username', None)
                    if not author:
                        author = j['author'].get('email', None)
                    if not author:
                        continue

                    for approval in j.get('approvals', []):
                        data = {'number': number,
                                'patchset': patchset,
                                'project': project,
                                'type': approval['type'],
                                'value': approval['value'],
                                'id': j['change']['id'],
                                'sha': j['patchSet']['revision']}
                        reviews.setdefault(author, [])
                        reviews[author].append(copy.copy(data))

                        data['comment'] = j['comment']
                        reviews_verbose.setdefault(author, [])
                        reviews_verbose[author].append(copy.copy(data))

                        desc = '%s:%s:%s' % (author, approval['type'],
                                             approval['value'])
                        if not desc in patches[patch_key][patchset]['reviews']:
                            patches[patch_key][patchset]['reviews'].append(
                                desc)

            except Exception, e:
                print 'Error: %s\n' % e
                print json.dumps(j, indent=4)
                sys.exit(0)

    with open('%s_reviews.json' % filename, 'w') as f:
        f.write(json.dumps(reviews, indent=4))
    with open('%s_reviews_verbose.json' % filename, 'w') as f:
        f.write(json.dumps(reviews_verbose, indent=4))

for patch_key in patches:
    if not os.path.exists(patch_key):
        os.makedirs(patch_key)
    for patchset in patches[patch_key]:
        with open('%s/%s.json' % (patch_key, patchset), 'w') as f:
            f.write(json.dumps(patches[patch_key][patchset], indent=4))

print 'Done'

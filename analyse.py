#!/usr/bin/python

import datetime
import json
import sys
import urllib


CI_SYSTEM = ['Jenkins',
             'turbo-hipster',
             'Hyper-V CI',
             'VMware Mine Sweeper',
             'Docker CI',
             'NEC OpenStack CI']


def read_remote_lines(url):
    remote = urllib.urlopen(url)
    data = ''
    while True:
        d = remote.read(100)
        if not d:
            break

        data += d

        if data.find('\n') != -1:
            elems = data.split('\n')
            for line in elems[:-1]:
                yield line
            data = elems[-1]

    if data:
        yield data


if __name__ == '__main__':
    patchsets = {}
    skipped_authors = {}
    day = datetime.datetime.now()
    day -= datetime.timedelta(days=7)

    while day < datetime.datetime.now():
        print 'Processing %s/%s/%s' % (day.year, day.month, day.day)
        for line in read_remote_lines('http://www.rcbops.com/gerrit/merged/'
                                      '%s/%s/%s'
                                      % (day.year, day.month, day.day)):
            try:
                j = json.loads(line)
            except:
                continue

            try:
                if not 'change' in j:
                    continue
                if j['change']['project'] != 'openstack/nova':
                    continue

                if j['type'] == 'patchset-created':
                    number = j['change']['number']
                    patchset = j['patchSet']['number']
                    timestamp = j['patchSet']['createdOn']
                    patchsets['%s,%s' % (number, patchset)] = \
                        {'__created__': timestamp}

                elif j['type'] == 'comment-added':
                    if not 'approvals' in j:
                        j['approvals'] = [{'type': 'CRVW', 'value': 0}]

                    author = j['author']['name']
                    if not author in CI_SYSTEM:
                        skipped_authors.setdefault(author, 0)
                        skipped_authors[author] += 1
                        continue

                    number = j['change']['number']
                    patchset = j['patchSet']['number']
                    timestamp = j['patchSet']['createdOn']

                    verified = []
                    for approval in j['approvals']:
                        verified.append('%s:%s' % (approval['type'],
                                                   approval.get('value')))

                    key = '%s,%s' % (number, patchset)
                    patchsets.setdefault(key, {})
                    patchsets[key][author] = (timestamp, verified)

                elif j['type'] in ['change-abandoned',
                                   'change-merged',
                                   'change-restored',
                                   'ref-updated']:
                    pass

                else:
                    print json.dumps(j, indent=4)
                    sys.exit(0)

            except Exception, e:
                print 'Error: %s\n' % e
                print json.dumps(j, indent=4)
                sys.exit(0)

        day += datetime.timedelta(days=1)

    # Write some json blobs, which are intended mostly for debugging
    with open('patchsets.json', 'w') as f:
        f.write(json.dumps(patchsets, indent=4))
    with open('skipped.json', 'w') as f:
        f.write(json.dumps(skipped_authors, indent=4))

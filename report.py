#!/usr/bin/python

import datetime
import json
import sys


if __name__ == '__main__':
    with open('patchsets.json') as f:
        patchsets = json.loads(f.read())

    # Summarize
    timeslots = {}
    for patchset in patchsets:
        if not '__created__' in patchsets[patchset]:
            continue
        created = patchsets[patchset]['__created__']

        created_dt = datetime.datetime.fromtimestamp(created)
        timeslot = datetime.datetime(created_dt.year,
                                     created_dt.month,
                                     created_dt.day,
                                     created_dt.hour).strftime('%Y%m%d %H%M')

        timeslots.setdefault(timeslot, {})
        timeslots[timeslot].setdefault('__total__', 0)
        timeslots[timeslot]['__total__'] += 1

        for author in patchsets[patchset]:
            if author == '__created__':
                continue

            author_vote = json.dumps((author, patchsets[patchset][author][1]))
            timeslots[timeslot].setdefault(author_vote, 0)
            timeslots[timeslot][author_vote] += 1

            #print '%s,%s,%s,%s' %(patchset,
            #                      author,
            #                      patchsets[patchset][author][0] - created,
            #                      patchsets[patchset][author][1])

    # Report
    for timeslot in sorted(timeslots.keys()):
        authors = {}
        for author_vote in timeslots[timeslot]:
            if author_vote == '__total__':
                continue

            try:
                author, vote = json.loads(author_vote)
                count = timeslots[timeslot][author_vote]

                authors.setdefault(author, {})
                authors[author].setdefault('+', 0)
                authors[author].setdefault('-', 0)
                authors[author].setdefault('0', 0)
                authors[author].setdefault('?', 0)

                clean_votes = []
                for single in vote:
                    if not single.endswith(':0'):
                        clean_votes.append(single)
                vote = clean_votes

                if len(vote) > 1:
                    print '*** Multiple vote %s ***' % vote
                    v = '?'
                elif len(vote) == 0:
                    v = '0'
                else:
                    vote = vote[0]
                    votetype, votevalue = vote.split(':')
                    if votevalue in ['1', '2']:
                        v = '+'
                    elif votevalue in ['-1', '-2']:
                        v = '-'
                    else:
                        v = '0'
                authors[author][v] += count

            except Exception, e:
                print '*** Could not decode %s (%s) ***' % (author_vote, e)

        sys.stdout.write('%s ' % timeslot)
        for author in authors:
            sys.stdout.write('%s(' % author)
            votes = []
            for vote in ['-', '0', '+', '?']:
                votes.append('%s' % authors[author][vote])
            sys.stdout.write(','.join(votes))
            sys.stdout.write(') ')
        sys.stdout.write('\n')

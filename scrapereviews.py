#!/usr/bin/python

# Scrape review information from gerrit

import datetime
import json
import time

import feedutils
import sql
import utility


def reviews():
    cursor = feedutils.GetCursor()

    day = datetime.datetime.now()
    day -= datetime.timedelta(days=7)

    while day < datetime.datetime.now():
        print 'Processing %s/%s/%s' % (day.year, day.month, day.day)
        data = utility.read_remote_file(
              'http://www.rcbops.com/gerrit/merged/%s/%s/%s_reviews.json'
              % (day.year, day.month, day.day))
        j = json.loads(data)

        for username in j:
            summary = {}
            for review in j[username]:
                summary.setdefault(review['project'], 0)
                summary.setdefault('__total__', 0)
                summary[review['project']] += 1
                summary['__total__'] += 1

            cursor.execute('delete from reviewsummary where '
                           'username="%s" and day=date(%s);'
                           %(username, day))
            cursor.execute('insert into reviewsummary'
                           '(day, username, data, epoch) '
                           'values (date(%s), "%s", \'%s\', %d);'
                           %(day, username, json.dumps(summary),
                             int(time.time())))
            cursor.execute('commit;')


if __name__ == '__main__':
    reviews()

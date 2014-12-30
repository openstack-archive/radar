#!/usr/bin/python

# Take gerrit status feeds and turn them into an RSS feed

import cgi
import datetime
import json
import random
import sys
import time
import MySQLdb

import feedutils
import sql


if __name__ == '__main__':
    print 'Content-Type: text/plain\r'
    print '\r'
    sys.stdout.flush()

    cursor = feedutils.GetCursor()
    form = cgi.FieldStorage()

    initial_size = 30

    if form.has_key('reviewers'):
        showusers = feedutils.ResolveGroupMembers(cursor,
                                                  form['reviewers'].value,
                                                  'reviewsummary',
                                                  initial_size)
    else:
        showusers = ['mikalstill']

    if form.has_key('project'):
        project = form['project'].value
    else:
        project = '__total__'

    last_time = feedutils.GetInitial('review', showusers, project,
                                     initial_size)
    feedutils.GetUpdates('review', showusers, project, last_time)

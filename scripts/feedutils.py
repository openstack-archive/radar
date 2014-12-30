#!/usr/bin/python

# Helpers for producing data feeds

import cgi
import datetime
import json
import random
import sys
import time
import MySQLdb

import sql

def SendPacket(packet):
    packet['timestamp'] = int(time.time())
    print json.dumps(packet)
    sys.stdout.flush()


def GetCursor():
    # Read config from a file
    with open('/srv/config/summaryfeed') as f:
        flags = json.loads(f.read())

    db = MySQLdb.connect(user = flags['dbuser'],
                         db = flags['dbname'],
                         passwd = flags['dbpassword'],
                         host = flags.get('dbhost', 'localhost'))
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
    return cursor


def SendGroups(cursor):
    groups = []
    cursor.execute('select * from groups;')
    for row in cursor:
      groups.append([row['name'], row['members'].split(' ')])
    SendPacket({'type': 'groups',
                'payload': groups})


def GetGroupMembers(cursor, groupname):
    members = []
    cursor.execute('select * from groups where name="%s";'
                   % groupname)
    if cursor.rowcount > 0:
      row = cursor.fetchone()
      for member in row['members'].split(' '):
        members.append(member)
    return members


def ResolveGroupMembers(cursor, usersliststring, table, window_size):
    showusers = []

    one_day = datetime.timedelta(days=1)
    start_of_window = datetime.datetime.now()
    start_of_window -= one_day * window_size

    for userish in usersliststring.lstrip(' ').split(' '):
        if userish.startswith('g:'):
            group_name = userish.split(':')[1]
            if group_name == 'all':
                cursor.execute('select distinct(username), max(day) from %s '
                               'where day > date(%s) group by username;'
                               %(table,
                                 sql.FormatSqlValue('timestamp',
                                                    start_of_window)))
                for row in cursor:
                    showusers.append(row['username'])
            else:
                for user in GetGroupMembers(cursor, group_name):
                    showusers.append(user)
        else:
            showusers.append(userish)

    if len(showusers) == 0:
        showusers = ['mikalstill']

    return showusers


def SendTriagers(cursor, window_size):
    SendUsers(cursor, window_size, 'bugtriagesummary')


def SendClosers(cursor, window_size):
    SendUsers(cursor, window_size, 'bugclosesummary')


def SendUsers(cursor, window_size, table, project=None):
    one_day = datetime.timedelta(days=1)
    start_of_window = datetime.datetime.now()
    start_of_window -= one_day * window_size

    plike = '%'
    if project:
        plike = '%%%s%%' % project

    all_reviewers = []
    cursor.execute('select distinct(username), max(day) from %s '
                   'where data like "%s" and day > date(%s) group by username;'
                   %(table, plike,
                     sql.FormatSqlValue('timestamp', start_of_window)))
    for row in cursor:
        all_reviewers.append((row['username'], row['max(day)'].isoformat()))
    SendPacket({'type': 'users-all',
                'payload': all_reviewers})


def SendKeepAlive():
    SendPacket({'type': 'keepalive'})


def SendDebug(message):
    SendPacket({'type': 'debug',
                'payload': message})


def GetInitial(eventname, showusers, project, initial_size):
    cursor = GetCursor()

    # Fetch the last seven days of results to start off with
    last_time = 0
    one_day = datetime.timedelta(days=1)

    SendGroups(cursor)
    SendUsers(cursor, initial_size, '%ssummary' % eventname, project=project)
    SendPacket({'type': 'users-present', 'payload': showusers})

    for username in showusers:
        day = datetime.datetime.now()
        day = datetime.datetime(day.year, day.month, day.day)

        day -= one_day * (initial_size - 1)
        for i in range(initial_size):
            timestamp = sql.FormatSqlValue('timestamp', day)
            cursor.execute('select * from %ssummary where username="%s" '
                           'and day=date(%s);'
                           %(eventname, username, timestamp))
            packet = {'type': 'initial-value',
                      'user': username,
                      'day': day.isoformat()}
            if cursor.rowcount > 0:
                row = cursor.fetchone()
                packet['payload'] = json.loads(row['data']).get(project, 0)
                packet['written-at'] = row['epoch']

                if row['epoch'] > last_time:
                    last_time = row['epoch']
            else:
                packet['payload'] = 0

            SendPacket(packet)
            day += one_day

    SendPacket({'type': 'initial-value-ends'})
    return last_time


def GetUpdates(eventname, showusers, project, last_time):
    while True:
        time.sleep(60)

        # Rebuild the DB connection in case the DB went away
        cursor = GetCursor()
        SendKeepAlive()
        SendDebug('Querying for updates after %d, server time %s'
                  %(last_time, datetime.datetime.now()))

        for username in showusers:
            ts = datetime.datetime.now()
            ts -= datetime.timedelta(days=5)
            cursor.execute('select * from %ssummary where username="%s" '
                           'and epoch > %d and day > date(%s);'
                           %(eventname, username, last_time,
                             sql.FormatSqlValue('timestamp', ts)))

            for row in cursor:
                SendPacket(
                    {'type': 'update-value',
                     'user': username,
                     'written-at': row['epoch'],
                     'day': row['day'].isoformat(),
                     'payload': json.loads(row['data']).get(project, 0)})

                if row['epoch'] > last_time:
                    last_time = row['epoch']

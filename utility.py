#!/usr/bin/python

import decimal
import types
import unicodedata
import urllib


def DisplayFriendlySize(bytes):
  """DisplayFriendlySize -- turn a number of bytes into a nice string"""

  t = type(bytes)
  if t != types.LongType and t != types.IntType and t != decimal.Decimal:
    return 'NotANumber(%s=%s)' %(t, bytes)

  if bytes < 1024:
    return '%d bytes' % bytes

  if bytes < 1024 * 1024:
    return '%d kb (%d bytes)' %((bytes / 1024), bytes)

  if bytes < 1024 * 1024 * 1024:
    return '%d mb (%d bytes)' %((bytes / (1024 * 1024)), bytes)

  return '%d gb (%d bytes)' %((bytes / (1024 * 1024 * 1024)), bytes)


def Normalize(value):
  normalized = unicodedata.normalize('NFKD', unicode(value))
  normalized = normalized.encode('ascii', 'ignore')
  return normalized


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


def read_remote_file(url):
    data = []
    for line in read_remote_lines(url):
        data.append(line)
    return '\n'.join(data)


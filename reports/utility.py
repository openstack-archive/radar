#!/usr/bin/python

import decimal
import types
import unicodedata


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

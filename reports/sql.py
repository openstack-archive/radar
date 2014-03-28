#!/usr/bin/python

# Some simple SQL helpers

import datetime
import utility
import unicodedata


class FormatException(Exception):
  """ FormatException -- Used for reporting failures for format DB values """


def FormatSqlValue(name, value):
  """FormatSqlValue -- some values get escaped for SQL use"""

  if type(value) == datetime.datetime:
    return ('STR_TO_DATE("%s", "%s")'
            %(value.strftime('%a, %d %b %Y %H:%M:%S'),
              '''%a, %d %b %Y %H:%i:%s'''))

  if name == 'date':
    return 'STR_TO_DATE("%s", "%s")' %(value, '''%a, %d %b %Y %H:%i:%s''')

  if type(value) == long or type(value) == int:
    return '%d' % value

  if value == '':
    return '""'

  if value is None:
    return 'NULL'

  try:
    return '"%s"' % utility.Normalize(value).replace('"', '""')
  except Exception, e:
    raise FormatException('Could not format string value %s = %s (%s)'
                          %(name, value, e))

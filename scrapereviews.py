#!/usr/bin/python

# Scrape review information from gerrit

import base64
import datetime
import hashlib
import json
import re
import sys
import time
import MySQLdb

import dbcachingexecute
import feedutils
import sql


def Reviews(component):
    cursor = feedutils.GetCursor()
    for l in dbcachingexecute.Execute(time.time() - 60,
                                      'gerrit_query_approvals_json',
                                      ('ssh -i ~/.ssh/id_gerrit '
                                       'review.openstack.org gerrit query '
                                       'project:%s '
                                       '--all-approvals --patch-sets '
                                       '--format JSON'),
                                      component, cleanup=True):

      try:
          d = json.loads(l)
      except:
          continue

      if d.has_key('id'):
          b64 = base64.encodestring(l)
          checksum = hashlib.sha1(l).hexdigest()
          last_updated = datetime.datetime.fromtimestamp(d['lastUpdated'])
          timestamp = sql.FormatSqlValue('timestamp', last_updated)
          insert = ('insert ignore into changes (changeid, timestamp, parsed, '
                    'checksum) values ("%s", %s, "%s", "%s");'
                    %(d['id'], timestamp, b64, checksum))
          cursor.execute(insert)
          if cursor.rowcount == 0:
              cursor.execute('select * from changes where changeid="%s";'
                             % d['id'])
              stored_checksum = cursor.fetchone()['checksum']
              if checksum != stored_checksum:
                  cursor.execute('delete from changes where changeid="%s";'
                                 % d['id'])
                  cursor.execute(insert)
          cursor.execute('commit;')

      for ps in d.get('patchSets', {}):
          patchset = ps.get('number')

          for review in ps.get('approvals', []):
              # Deliberately leave the timezone alone here so its consistant
              # with reports others generate.
              updated_at = datetime.datetime.fromtimestamp(review['grantedOn'])
              username = review['by'].get('username', 'unknown')

              if username in ['jenkins', 'smokestack']:
                  continue

              timestamp = sql.FormatSqlValue('timestamp', updated_at)
              score = review.get('value', 0)
              cursor.execute('insert ignore into reviews '
                             '(changeid, username, timestamp, day, component, '
                             'patchset, score) '
                             'values ("%s", "%s", %s, date(%s), "%s", %s, %s);'
                             %(d['id'], username, timestamp, timestamp,
                               component, patchset, score))
              if cursor.rowcount > 0:
                  # This is a new review, we assume we're the only writer
                  print 'New review from %s' % username
                  cursor.execute('select * from reviewsummary where '
                                 'username="%s" and day=date(%s);'
                                 %(username, timestamp))
                  if cursor.rowcount > 0:
                      row = cursor.fetchone()
                      summary = json.loads(row['data'])
                  else:
                      summary = {}

                  summary.setdefault(component, 0)
                  summary.setdefault('__total__', 0)
                  summary[component] += 1
                  summary['__total__'] += 1

                  cursor.execute('delete from reviewsummary where '
                                 'username="%s" and day=date(%s);'
                                 %(username, timestamp))
                  cursor.execute('insert into reviewsummary'
                                 '(day, username, data, epoch) '
                                 'values (date(%s), "%s", \'%s\', %d);'
                                 %(timestamp, username,
                                   json.dumps(summary),
                                   int(time.time())))

              cursor.execute('commit;')


if __name__ == '__main__':
    Reviews('openstack/heat-cfntools')
    Reviews('openstack/heat')
    Reviews('openstack/heat-templates')
    Reviews('openstack/python-heatclient')
    Reviews('openstack-infra/askbot-theme')
    Reviews('openstack-infra/devstack-gate')
    Reviews('openstack-infra/gear')
    Reviews('openstack-infra/gerrit')
    Reviews('openstack-infra/gerritbot')
    Reviews('openstack-infra/gerritlib')
    Reviews('openstack-infra/jeepyb')
    Reviews('openstack-infra/gitdm')
    Reviews('openstack-infra/git-review')
    Reviews('openstack-infra/jenkins-job-builder')
    Reviews('openstack-infra/lodgeit')
    Reviews('openstack-infra/meetbot')
    Reviews('openstack-infra/nose-html-output')
    Reviews('openstack-infra/puppet-apparmor')
    Reviews('openstack-infra/puppet-dashboard')
    Reviews('openstack-infra/puppet-vcsrepo')
    Reviews('openstack-infra/reviewday')
    Reviews('openstack-infra/statusbot')
    Reviews('openstack-infra/zmq-event-publisher')
    Reviews('openstack-infra/zuul')
    Reviews('openstack-dev/devstack')
    Reviews('openstack-dev/grenade')
    Reviews('openstack-dev/hacking')
    Reviews('openstack-dev/pbr')
    Reviews('openstack-dev/openstack-nose')
    Reviews('openstack-dev/openstack-qa')
    Reviews('openstack-dev/sandbox')
    Reviews('openstack/api-site')
    Reviews('openstack/ceilometer')
    Reviews('openstack/cinder')
    Reviews('openstack/compute-api')
    Reviews('openstack/glance')
    Reviews('openstack/horizon')
    Reviews('openstack/identity-api')
    Reviews('openstack/image-api')
    Reviews('openstack/keystone')
    Reviews('openstack/netconn-api')
    Reviews('openstack/nova')
    Reviews('openstack/object-api')
    Reviews('openstack/openstack-chef')
    Reviews('openstack-infra/config')
    Reviews('openstack/openstack-manuals')
    Reviews('openstack/openstack-planet')
    Reviews('openstack/oslo-incubator')
    Reviews('openstack/oslo.config')
    Reviews('openstack/python-ceilometerclient')
    Reviews('openstack/python-cinderclient')
    Reviews('openstack/python-glanceclient')
    Reviews('openstack/python-keystoneclient')
    Reviews('openstack/python-novaclient')
    Reviews('openstack/python-openstackclient')
    Reviews('openstack/python-quantumclient')
    Reviews('openstack/python-swiftclient')
    Reviews('openstack/quantum')
    Reviews('openstack/requirements')
    Reviews('openstack/swift')
    Reviews('openstack/tempest')
    Reviews('openstack/volume-api')
    Reviews('stackforge/MRaaS')
    Reviews('stackforge/diskimage-builder')
    Reviews('stackforge/tripleo-image-elements')
    Reviews('stackforge/healthnmon')
    Reviews('stackforge/libra')
    Reviews('stackforge/python-libraclient')
    Reviews('stackforge/marconi')
    Reviews('stackforge/moniker')
    Reviews('stackforge/python-monikerclient')
    Reviews('stackforge/python-reddwarfclient')
    Reviews('stackforge/reddwarf')
    Reviews('stackforge/reddwarf-integration')
    Reviews('stackforge/bufunfa')
    Reviews('stackforge/kwapi')
    Reviews('stackforge/climate')
    Reviews('openstack-infra/gearman-plugin')
    Reviews('stackforge/packstack')
    Reviews('stackforge/database-api')
    Reviews('stackforge/anvil')
    Reviews('stackforge/savanna')
    Reviews('stackforge/python-savannaclient')
    Reviews('stackforge/os-config-applier')
    Reviews('stackforge/os-refresh-config')
    Reviews('stackforge/puppet-cinder')
    Reviews('stackforge/puppet-glance')
    Reviews('stackforge/puppet-horizon')
    Reviews('stackforge/puppet-keystone')
    Reviews('stackforge/puppet-nova')
    Reviews('stackforge/puppet-openstack')
    Reviews('stackforge/puppet-openstack_dev_env')
    Reviews('stackforge/puppet-swift')
    Reviews('stackforge/puppet-quantum')
    Reviews('stackforge/opencafe')
    Reviews('stackforge/cloudcafe')
    Reviews('stackforge/cloudroast')

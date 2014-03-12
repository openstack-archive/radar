#!/usr/bin/python

import copy
import datetime
import json
import sys
import time

import conf

def patch_list_as_html(l):
    out = []
    for p in sorted(l):
        number, patch = p.split(',')
        out.append('<a href="http://review.openstack.org/#/c/%s/%s">%s,%s</a>'
                   % (number, patch, number, patch))
    return ', '.join(out)


def report(project_filter, user_filter, prefix):
    with open('patchsets.json') as f:
        patchsets = json.loads(f.read())

    if not user_filter:
        user_filter = conf.CI_SYSTEM[prefix]
    elif user_filter and not 'Jenkins' in user_filter:
        user_filter_new = ['Jenkins']
        user_filter_new.extend(user_filter)
        user_filter = user_filter_new

    user_filter_without_jenkins = copy.copy(user_filter)
    user_filter_without_jenkins.remove('Jenkins')
        
    # This is more complicated than it looks because we need to handle
    # patchsets which are uploaded so rapidly that older patchsets aren't
    # finished testing.
    total_patches = 0
    total_votes = {}
    missed_votes = {}
    sentiments = {}
    passed_votes = {}
    failed_votes = {}
    unparsed_votes = {}

    for number in patchsets:
        if patchsets[number].get('__exemption__'):
            continue

        if project_filter != '*':
            if patchsets[number].get('__project__') != project_filter:
                continue
        
        patches = sorted(patchsets[number].keys())
        valid_patches = []

        # Determine how long a patch was valid for. If it wasn't valid for
        # at least three hours, disgard.
        for patch in patches:
            if not '__created__' in patchsets[number][patch]:
                continue

            uploaded = datetime.datetime.fromtimestamp(
                patchsets[number][patch]['__created__'])
            obsoleted = datetime.datetime.fromtimestamp(
                patchsets[number].get(str(int(patch) + 1), {}).get(
                '__created__', time.time()))
            valid_for = obsoleted - uploaded

            if valid_for < datetime.timedelta(hours=3):
                continue

            matched_authors = 0
            for author in patchsets[number][patch]:
                if author == '__created__':
                    continue

                if author not in user_filter_without_jenkins:
                    continue

                matched_authors += 1

            if matched_authors == 0:
                continue

            valid_patches.append(patch)

        total_patches += len(valid_patches)

        for patch in valid_patches:
            for author in patchsets[number][patch]:
                if author == '__created__':
                    continue

                if author not in user_filter:
                    continue

                total_votes.setdefault(author, 0)
                total_votes[author] += 1

                for vote, msg, sentiment in patchsets[number][patch][author]:
                    if sentiment.startswith('Positive'):
                        passed_votes.setdefault(author, 0)
                        passed_votes[author] += 1
                    elif sentiment.startswith('Negative'):
                        failed_votes.setdefault(author, 0)
                        failed_votes[author] += 1
                    else:
                        unparsed_votes.setdefault(author, 0)
                        unparsed_votes[author] += 1
                    
                    sentiments.setdefault(author, {})
                    sentiments[author].setdefault(sentiment, [])
                    sentiments[author][sentiment].append(
                        '%s,%s' % (number, patch))

            for author in user_filter:
                if not author in patchsets[number][patch]:
                    missed_votes.setdefault(author, [])
                    missed_votes[author].append('%s,%s' % (number, patch))

    with open('%s-cireport.html' % prefix, 'w') as f:
        f.write('<b>Valid patches in the last seven days: %d</b><ul>'
                % total_patches)
        for author in user_filter:
            if not author in total_votes:
                f.write('<li><font color=blue>No votes recorded for '
                        '<b>%s</b></font></li>'
                        % author)
                continue
            
            percentage = (total_votes[author] * 100.0 / total_patches)
            
            if percentage < 95.0:
                f.write('<font color=red>')
                
            passed = passed_votes.get(author, 0)
            failed = failed_votes.get(author, 0)
            unparsed = unparsed_votes.get(author, 0)
            total = passed + failed + unparsed
            pass_percentage = passed * 100.0 / total
            fail_percentage = failed * 100.0 / total
            unparsed_percentage = unparsed * 100.0 / total
            f.write('<li><b>%s</b> voted on %d patchsets (%.02f%%), '
                    'passing %d (%.02f%%), failing %s (%.02f%%) and '
                    'unparsed %d (%.02f%%)'
                    % (author, total_votes[author], percentage, passed,
                       pass_percentage, failed, fail_percentage, unparsed,
                        unparsed_percentage))
                
            if percentage < 95.0:
                  f.write('</font>')

            f.write('</li><ul><li>Missed %d: %s</li>'
                    '<li>Sentiment:</li><ul>'
                    % (len(missed_votes.get(author, [])),
                       patch_list_as_html(
                           missed_votes.get(author, []))))
            for sentiment in conf.SENTIMENTS:
                count = len(sentiments.get(author, {}).get(
                    sentiment, []))
                if count > 0:
                    f.write('<li>%s: %d' % (sentiment, count ))
                    if sentiment != 'Positive':
                        f.write('(%s)</li>'
                                % patch_list_as_html(
                                    sentiments[author][sentiment]))
                f.write('</li>')
            f.write('</ul></ul>')
        f.write('</ul><p>What is this report? Why is it so wrong? This report is a quick hack done by Michael Still to visualize the performance of CI systems voting on OpenStack changes. For help, please email him at mikal@stillhq.com. This report was generated at %s.</p>' % datetimedatetime.now())


if __name__ == '__main__':
    report('openstack/nova', None, 'nova')
    report('openstack/neutron', None, 'neutron')

    for user in conf.CI_USERS:
        report('*', [user], user.replace(' ', '_'))

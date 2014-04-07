#!/usr/bin/python

import copy
import datetime
import json
import sys
import time
from collections import namedtuple


import conf


def css():
    with open('rcbau.css', 'w') as f:
        f.write("""
                body {
                    font-size:75%;
                    color:#222;
                    background:#fff;
                    font-family:"Helvetica Neue", Arial, Helvetica, sans-serif;
                }

                h3.failing { color: red; }
                h3.nonvoting { color: blue; }

                div.graph { float:left; width:25em; height:300px; }
                div.small_graph { width:15em; height:150px;  }
                div.patchsets_list { width:50em; float:left }
                div.clear_float { clear:both }


                a.ui-tabs-anchor div {
                    color: blue;
                    text-align: center;
                    text-decoration: underline;
                }
                """)

        
def patch_list_as_html(l):
    out = []
    for p in sorted(l):
        number, patch = p.split(',')
        out.append('<a href="http://review.openstack.org/#/c/%s/%s">%s,%s</a>'
                   % (number, patch, number, patch))
    return ', '.join(out)


def pie_chart(author):
    name = author.name.replace(' ', '-')
    passed = author.passed
    failed = author.failed
    missed = len(author.missed_votes)
    
    return """
                $('#{name}-graph').highcharts({{
                    chart: {{
                        plotBackgroundColor: null,
                        plotBorderWidth: 0,
                        plotShadow: false
                    }},
                    colors: [ 'green', 'red', 'yellow' ],
                    title: {{
                        text: 'Results',
                        align: 'center',
                        verticalAlign: 'middle',
                        y: 50
                    }},
                    tooltip: {{
                        pointFormat: 
                        '{{series.name}}: <b>{{point.percentage:.1f}}%</b>'
                    }},
                    plotOptions: {{
                        pie: {{
                            dataLabels: {{
                                enabled: true,
                                distance: -50,
                                style: {{
                                    fontWeight: 'bold',
                                    color: 'white',
                                    textShadow: '0px 1px 2px black'
                                }}
                            }},
                            startAngle: -90,
                            endAngle: 90,
                            center: ['50%', '75%']
                        }}
                    }},
                    series: [{{
                        type: 'pie',
                        name: 'Results',
                        innerSize: '50%',
                        data: [
                            ['Passed', {passed}],
                            ['Failed', {failed}],
                            ['Missed', {missed}]
                        ]
                    }}]
                }});
    """.format(name=name, passed=passed, failed=failed, missed=missed)


def small_pie_chart(author):
    name = author.name.replace(' ', '-') + '-small'
    
    if author.total:
        passed = author.passed
        failed = author.failed
        missed = len(author.missed_votes)
    else:
        passed = 0
        failed = 0
        missed = 1

    graph = """
                $('#{name}-graph').highcharts({{
                    chart: {{
                        plotBackgroundColor: null,
                        plotBorderWidth: 0,
                        plotShadow: false
                    }},
                    colors: [ 'green', 'red', 'yellow' ],
                    title: {{
                        text: '',
                        align: 'center',
                        verticalAlign: 'middle',
                        y: 50
                    }},
                    tooltip: {{
                        pointFormat: 
                        '{{series.name}}: <b>{{point.percentage:.1f}}%</b>'
                    }},
                    plotOptions: {{
                        pie: {{
                            dataLabels: {{
                                enabled: false
                            }},
                            startAngle: -90,
                            endAngle: 90,
                            center: ['50%', '75%']
                        }}
                    }},
                    series: [{{
                        type: 'pie',
                        innerSize: '50%',
                        data: [
                            ['Passed', {passed}],
                            ['Failed', {failed}],
                            ['Missed', {missed}]
                        ]
                    }}]
                }});
                """
    return graph.format(
        author=author, 
        name=name, 
        passed=passed, 
        failed=failed, 
        missed=missed
    )


def templated_report(**kwargs):
        import os

        path = os.path.dirname(__file__)

        from chameleon import PageTemplateLoader
        templates = PageTemplateLoader(os.path.join(path, "templates"))

        template = templates['report.pt']

        return template(**kwargs)


def report(project_filter, user_filter, prefix, fname):
    with open(fname) as f:
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
                patchsets[number][patch]['__created__']
            )
            
            obsoleted = datetime.datetime.fromtimestamp(
                patchsets[number].get(
                    str(
                        int(patch) + 1), {}
                    ).get(
                        '__created__', 
                        time.time()
                    )
            )
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

    charts = []
    small_charts = []
    authors = []
    Author = namedtuple(
        'Author', 
        [
            'name',
            'percentage',
            'passed',
            'failed',
            'unparsed',
            'total',
            'pass_percentage',
            'fail_percentage',
            'unparsed_percentage',
            'missed_votes',
            'sentiments'
        ]
    )
    
    Patch = namedtuple(
        'Patch',
        'number patch'
    )
    
    for user in user_filter:
        passed = passed_votes.get(user, 0)
        failed = failed_votes.get(user, 0)
        unparsed = unparsed_votes.get(user, 0)
        total = passed + failed + unparsed
        user_sentiments = sentiments.get(user, {})
        
        for sentiment in user_sentiments:
            patches = []
            for patch in user_sentiments[sentiment]:
                patch, number = patch.split(',')
                patches.append(Patch(patch, number))
                
            user_sentiments[sentiment] = patches
        
        missed = []
        for missed_vote in missed_votes.get(user, []):
            patch, number = missed_vote.split(',')
            missed.append(Patch(patch, number))
                        
        if user in total_votes:
            authors.append(
                Author(
                    name=user,
                    percentage=round(
                        total_votes[user] * 100.0 / total_patches, 2
                        ),
                    passed=passed, 
                    failed=failed,
                    unparsed=unparsed,
                    total=total,
                    pass_percentage=round(passed * 100.0 / total, 2),
                    fail_percentage=round(failed * 100.0 / total, 2),
                    unparsed_percentage=round(unparsed * 100.0 / total, 2),
                    missed_votes=missed,
                    sentiments=user_sentiments
                )
            )
            charts.append(pie_chart(authors[-1]))
            small_charts.append(small_pie_chart(authors[-1]))
        else:
            authors.append(
                Author(
                    name=user,
                    percentage=None,
                    passed=None,
                    failed=None,
                    unparsed=None,
                    total=None,
                    pass_percentage=None,
                    fail_percentage=None,
                    unparsed_percentage=None,
                    missed_votes=None,
                    sentiments=None
                )
            )     
            small_charts.append(small_pie_chart(authors[-1]))
            
    report = templated_report(
        total_patches=total_patches,
        authors=authors,
        now=datetime.datetime.now(),
        missed_votes=missed_votes,
        sentiments=conf.SENTIMENTS,
        total_votes=total_votes,
        charts=charts,
        small_charts=small_charts
    )
    
    with open('%s-cireport.html' % prefix, 'w') as f:
        f.write(report)


if __name__ == '__main__':
    
    if len(sys.argv) > 1:        
        fname = sys.argv[1]
    else:
        fname = 'patchsets.json'
        
    css()
        
    report('openstack/nova', None, 'nova', fname)
    report('openstack/neutron', None, 'neutron', fname)

    for user in conf.CI_USERS:
        report('*', [user], user.replace(' ', '_'), fname)

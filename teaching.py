import collections
import datetime
from jinja2 import Template

from py4hy import people, courses

import argparse

parser = argparse.ArgumentParser(description="Produce teaching schedule for an organisational unit at University of Helsinki.")
parser.add_argument('organization_id', type=int, help='organization ID number')
parser.add_argument('--year', dest='year', type = int, default=courses._guess_study_year(), help='year of data production')
parser.add_argument('--output', dest='output', type = str, default='./', help='where output is stored')

args = parser.parse_args()

year = args.year

## people working in the organisation
staff = people.by_organisation( [ args.organization_id ] )

names = map( lambda person: person['firstnames'] + ' ' + person['lastname'], staff )
names = list( names )

staff_courses = {}

for name in names:
    for course in courses.search( name, academic_year = year ):
        staff_courses[ course['curId'] ] = course

staff_courses = staff_courses.values()

by_starting_time = collections.defaultdict( list )

for course in staff_courses:

    teachers = []
    for set in course['studyGroupSets']:
        for group in set['studySubGroups']:
            teachers += group['teacherNames']

    course['teachers'] = list( map( lambda x: x.replace('␟', '').strip() , teachers ) )

    ## seems to be only direct names at this time, no language variants.
    course['clean_name'] = course['name'] # ['en'] if 'en' in course['name'] else course['name']['fi']

    course['start_date'] = datetime.datetime.strptime( course['activityPeriod']['startDate'], '%Y-%m-%d' )
    course['end_date'] = datetime.datetime.strptime( course['activityPeriod']['endDate'], '%Y-%m-%d' )

    starting = course['start_date'].replace(day=1)

    by_starting_time[ starting ].append( course )

data = list( by_starting_time.items() )
data.sort( key = lambda x: x[0] )

template = Template( open('courses_year.html').read() )
open( args.output + str( year ) + '.html', 'w').write( template.render( data = data ) )

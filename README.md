# Canvas-tools
Tools for use with Instructure.com's Canvas LMS. These tools
are intended to be examples of how one can use the Canvas Restful API and to
provide some useful functionality (mainly for teachers).

Programs can be called with the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program.

Additionally, programs can be called with an alternative configuration file using the syntax: --config FILE

for example:  --config config-test.json

See the default-config.json file for an example of the structure of this file. Replace the string xxx by your access token and replace the string yyy.instructure.com with the name of the server where your Canvas LMS is running.

======================================================================
## list_your_courses_JSON.py

Purpose: To list the courses of the user runinng the program

Input: none
```
list_your_courses_JSON.py
```

Output: outputs JSON for user's courses

Example (edited to show only some of the output):
```
list_your_courses_JSON.py
[   {   'account_id': 42,
        'apply_assignment_group_weights': False,
        'blueprint': False,
        'calendar': {   'ics': 'https://kth.instructure.com/feeds/calendars/course_tvlR3Myd7jh5GZ71BV44uXb1WkYfpzq0lHCBJ7hR.ics'},
        'course_code': 'Chip',
        'created_at': '2016-06-10T07:58:47Z',
        'default_view': 'wiki',
        'end_at': None,
        'enrollment_term_id': 1,
        'enrollments': [   {   'enrollment_state': 'active',
                               'role': 'TeacherEnrollment',
                               'role_id': 4,
                               'type': 'teacher',
                               'user_id': 29}],
        'grading_standard_id': 40,
        'hide_final_grades': False,
        'id': 11,
        'integration_id': None,
        'is_public': True,
        'is_public_to_auth_users': False,
        'locale': 'en',
        'name': "Chip's sandbox",
        'original_name': 'Chip sandbox',
        'public_syllabus': True,
        'public_syllabus_to_auth': False,
        'restrict_enrollments_to_course_dates': False,
        'root_account_id': 1,
        'sis_course_id': None,
        'start_at': '2016-08-13T11:15:00Z',
        'storage_quota_mb': 5000,
        'time_zone': 'Europe/Stockholm',
        'uuid': 'tvlR3Myd7jh5GZ71BV44uXb1WkYfpzq0lHCBJ7hR',
        'workflow_state': 'available'},
        'workflow_state': 'unpublished'}]
```

## list_your_courses.py

Purpose: To list the courses of the user runinng the program

Input: none
```
list_your_courses.py
```

Output: outputs a file (courses-self.xlsx) containing a spreadsheet of the user's courses

```
list_your_courses.py
```

## users-in-course.py

Purpose: To get a list of the users in a course together with their sections and avatars

Input:
```
users-in-course.py course_id
```

Output: XLSX spreadsheet with textual section names and URL to user's avatar

Note that getting the avatars takes some time, hence this is optional

Examples:
```
users-in-course.py --config config-test.json 6434

users-in-course.py --config config-test.json --avatar 6434

users-in-course.py --config config-test.json --avatar -p 11

To make images 90x90 pixels in size:
  users-in-course.py --config config-test.json --avatar -p -s 90 11
```

## modules-in-course.py

Purpose: To list the modules in a course in a spreadsheet

Input: course_id
```
modules-in-course.py course_id
```

Output: outputs a spreadsheet named 'modules-'+course_id+'.xlsx'

Examples:
```
modules-in-course.py 11

modules-in-course.py --config config-test.json 11
```

## modules-items-in-course.py
Purpose: To list the module items in a course in a spreadsheet

Input: course_id
```
module-items-in-course.py course_id
```

Output: outputs a spreadsheet named 'module-items-'+course_id+'.xlsx'

Examples:
```
module-items-in-course.py 11

module-items-in-course.py --config config-test.json 11
```

## assignments-in-course.py

Purpose: To list the assignments in a course in a spreadsheet

Input: course_id
```
assignments-in-course.py course_id
```

Output: outputs a spreadsheet named 'assignments-'+course_id+'.xlsx'

Examples:
```
assignments-in-course.py 11

assignments-in-course.py --config config-test.json 11
```

## quizzes-in-course.py

Purpose: To list the quizzes in a course in a spreadsheet

Input: course_id
```
quizzes-in-course.py course_id
```

Output: outputs a spreadsheet named 'quizzes-'+course_id+'.xlsx'

Examples:
```
quizzes-in-course.py 11

quizzes-in-course.py --config config-test.json 11
```

## custom-columns-in-course.py

Purpose: To list the custom columns in a spreadsheet

Input:
```
custom-columns-in-course.py course_id
```

Example:
```
custom-columns-in-course.py 1585
```

## delete-custom-columns-in-course.py

Purpose: To delete a custom column or all custom columns from a course

Input:
```
To delete a specific custom column:
  delete-custom-columns-in-course.py course_id column_id

To delete aall custom column:
  delete-custom-columns-in-course.py -a course_id

```

Examples:
```
Delete one column:
  delete-custom-columns-in-course.py 12683 1118

Delete all columns:
  delete-custom-columns-in-course.py -v --config config-test.json -a 12683
```


## create-sections-in-course.py

Purpose: To create sections in a course

Input:
```
create-sections-in-course.py course_id [section_name]  [section_name]  [section_name] ...
```

Output: None

Example:
```
create-sections-in-course.py --config config-test.json 12683  'Test section'  'Test section2'
```


## delete-sections-in-course.py

Purpose: To delete indicated section(s) of a course

Input:
```
delete-sections-in-course.py course_id section_id
```

Output: deleting section id=NNNN with name=SSSSSS

Note 

Example:
```
delete-sections-in-course.py -v --config config-test.json 12683 16164

To delete all sections:
./delete-sections-in-course.py -a --config config-test.json 12683
```

## my-files.py

Purpose: To output a XLSX spreadsheet of the files for the user running the program

Input:
```
./my-files.py
```

Output: none

Example:
```
    ./my-files.py

    ./my-files.py --config config-test.json 11

for testing - skips some files:
   ./my-files.py -t 

    ./my-files.py -t --config config-test.json

```

## create-fake-users-in-course.py
Purpose: To create a set of fake users in a Canvas instance and enroll them in a course

Input:
```
./create-fake-users-in-course.py account_id course_id
```

Output: nothing

Example:
```
./create-fake-users-in-course.py 1 4

./create-fake-users-in-course.py --config config-test.json 1 4
```


## insert_AFPFFx_grading_standards.py

Purpose: To insert an A-F and Fx grading scheme, as well as a P/F and Fx grading scheme in either a course or an account.

Input:
```
insert_AFPFFx_grading_standards.py -a account_id
  or
insert_AFPFFx_grading_standards.py    course_id

```

Output: outputs a little information as it works

Examples:
```
insert_AFPFFx_grading_standards.py -v 11
insert_AFPFFx_grading_standards.py -v --config config-test.json 11

```
 
## custom-data-for-users-in-course.py

Purpose: To display custom data that is stored with a user in Canvas.

Input:
```
./custom-data-for-users-in-course.py course_id

the name space is 'se.kth.canvas-app.program_of_study'
the scope is 'program_of_study'

```

Output: the custom data associated with the name space and scope for each user in the selected course

Examples:
```
 ./custom-data-for-users-in-course.py 4

 ./custom-data-for-users-in-course.py --config config-test.json 4

Can be used With the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas in containers in a VM.

./custom-data-for-users-in-course.py -v 4
ARGV      : ['-v', '4']
VERBOSE   : True
REMAINING : ['4']
Configuration file : None
url: http://canvas.docker/api/v1/courses/4/enrollments
result of getting enrollments: [{"id":4,"user_id":3,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:13:42Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/3","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z1","html_url":"http://canvas.docker/courses/4/users/3","user":{"id":3,"name":"Ann FakeStudent","created_at":"2019-01-30T15:13:31+01:00","sortable_name":"FakeStudent, Ann","short_name":"Ann","sis_user_id":"z1","integration_id":null,"sis_import_id":null,"login_id":"s1"}},{"id":5,"user_id":4,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:15:56Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/4","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z2","html_url":"http://canvas.docker/courses/4/users/4","user":{"id":4,"name":"Bertil FakeStudent","created_at":"2019-01-30T15:13:32+01:00","sortable_name":"FakeStudent, Bertil","short_name":"Bertil","sis_user_id":"z2","integration_id":null,"sis_import_id":null,"login_id":"s2"}},{"id":6,"user_id":5,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:15:56Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/5","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z3","html_url":"http://canvas.docker/courses/4/users/5","user":{"id":5,"name":"Cenric FakeStudent","created_at":"2019-01-30T15:13:33+01:00","sortable_name":"FakeStudent, Cenric","short_name":"Cenric","sis_user_id":"z3","integration_id":null,"sis_import_id":null,"login_id":"s3"}},{"id":7,"user_id":6,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:15:57Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/6","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z4","html_url":"http://canvas.docker/courses/4/users/6","user":{"id":6,"name":"David FakeStudent","created_at":"2019-01-30T15:13:34+01:00","sortable_name":"FakeStudent, David","short_name":"David","sis_user_id":"z4","integration_id":null,"sis_import_id":null,"login_id":"s4"}},{"id":8,"user_id":7,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:15:58Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":"2019-02-06T14:53:12Z","last_attended_at":null,"total_activity_time":77235,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/7","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z5","html_url":"http://canvas.docker/courses/4/users/7","user":{"id":7,"name":"Ellen FakeStudent","created_at":"2019-01-30T15:13:34+01:00","sortable_name":"FakeStudent, Ellen","short_name":" Ellen","sis_user_id":"z5","integration_id":null,"sis_import_id":null,"login_id":"s5"}},{"id":9,"user_id":8,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:15:58Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/8","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z6","html_url":"http://canvas.docker/courses/4/users/8","user":{"id":8,"name":"Fran FakeStudent","created_at":"2019-01-30T15:13:35+01:00","sortable_name":"FakeStudent, Fran","short_name":"Fran","sis_user_id":"z6","integration_id":null,"sis_import_id":null,"login_id":"s6"}},{"id":10,"user_id":9,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:15:59Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/9","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z7","html_url":"http://canvas.docker/courses/4/users/9","user":{"id":9,"name":"Gordon FakeStudent","created_at":"2019-01-30T15:13:36+01:00","sortable_name":"FakeStudent, Gordon","short_name":"Gordon","sis_user_id":"z7","integration_id":null,"sis_import_id":null,"login_id":"s7"}},{"id":11,"user_id":10,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:15:59Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/10","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z8","html_url":"http://canvas.docker/courses/4/users/10","user":{"id":10,"name":"Håkan FakeStudent","created_at":"2019-01-30T15:13:37+01:00","sortable_name":"FakeStudent, Håkan","short_name":"Håkan","sis_user_id":"z8","integration_id":null,"sis_import_id":null,"login_id":"s8"}},{"id":12,"user_id":11,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:16:00Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":null,"last_attended_at":null,"total_activity_time":0,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/11","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z9","html_url":"http://canvas.docker/courses/4/users/11","user":{"id":11,"name":"Ibǘy FakeStudent","created_at":"2019-01-30T15:13:39+01:00","sortable_name":"FakeStudent, Ibǘy","short_name":"Ibǘy","sis_user_id":"z9","integration_id":null,"sis_import_id":null,"login_id":"s9"}},{"id":13,"user_id":12,"course_id":4,"type":"StudentEnrollment","created_at":"2019-01-30T14:16:00Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":"2019-02-06T14:00:42Z","last_attended_at":null,"total_activity_time":173942,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/12","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z10","html_url":"http://canvas.docker/courses/4/users/12","user":{"id":12,"name":"James FakeStudent","created_at":"2019-01-30T15:13:40+01:00","sortable_name":"FakeStudent, James","short_name":"James","sis_user_id":"z10","integration_id":null,"sis_import_id":null,"login_id":"s10"}},{"id":15,"user_id":14,"course_id":4,"type":"StudentEnrollment","created_at":"2019-02-06T09:18:21Z","updated_at":"2019-02-06T09:19:20Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":"2019-02-06T14:22:28Z","last_attended_at":null,"total_activity_time":8471,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/14","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z13","html_url":"http://canvas.docker/courses/4/users/14","user":{"id":14,"name":"Quentin FakeStudent","created_at":"2019-02-06T10:12:16+01:00","sortable_name":"FakeStudent, Quentin","short_name":"Quentin FakeStudent","sis_user_id":"z13","integration_id":null,"sis_import_id":null,"login_id":"s13"}},{"id":14,"user_id":13,"course_id":4,"type":"StudentViewEnrollment","created_at":"2019-02-02T11:36:20Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"StudentEnrollment","role_id":3,"last_activity_at":"2019-02-03T09:47:40Z","last_attended_at":null,"total_activity_time":13288,"sis_import_id":null,"grades":{"html_url":"http://canvas.docker/courses/4/grades/13","current_score":null,"current_grade":null,"final_score":null,"final_grade":null,"unposted_current_score":null,"unposted_current_grade":null,"unposted_final_score":null,"unposted_final_grade":null},"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":null,"html_url":"http://canvas.docker/courses/4/users/13","user":{"id":13,"name":"Test Student","created_at":"2019-02-02T12:36:19+01:00","sortable_name":"Student, Test","short_name":"Test Student","sis_user_id":null,"integration_id":null,"sis_import_id":null,"login_id":"8054dc7dea06ac29b246be030ededb30a6197af0"}},{"id":3,"user_id":1,"course_id":4,"type":"TeacherEnrollment","created_at":"2018-12-23T17:45:34Z","updated_at":"2019-02-02T14:07:49Z","associated_user_id":null,"start_at":null,"end_at":null,"course_section_id":2,"root_account_id":1,"limit_privileges_to_course_section":false,"enrollment_state":"active","role":"TeacherEnrollment","role_id":4,"last_activity_at":"2019-02-06T19:25:13Z","last_attended_at":null,"total_activity_time":445591,"sis_import_id":null,"sis_account_id":null,"sis_course_id":null,"course_integration_id":null,"sis_section_id":null,"section_integration_id":null,"sis_user_id":"z0","html_url":"http://canvas.docker/courses/4/users/1","user":{"id":1,"name":"chip.maguire@gmail.com","created_at":"2018-12-12T12:08:59+01:00","sortable_name":"chip.maguire@gmail.com","short_name":"chip.maguire@gmail.com","sis_user_id":"z0","integration_id":null,"sis_import_id":null,"login_id":"chip.maguire@gmail.com"}}]
[{'id': 4, 'user_id': 3, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:13:42Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/3', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z1', 'html_url': 'http://canvas.docker/courses/4/users/3', 'user': {'id': 3, 'name': 'Ann FakeStudent', 'created_at': '2019-01-30T15:13:31+01:00', 'sortable_name': 'FakeStudent, Ann', 'short_name': 'Ann', 'sis_user_id': 'z1', 'integration_id': None, 'sis_import_id': None, 'login_id': 's1'}}, {'id': 5, 'user_id': 4, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:15:56Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/4', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z2', 'html_url': 'http://canvas.docker/courses/4/users/4', 'user': {'id': 4, 'name': 'Bertil FakeStudent', 'created_at': '2019-01-30T15:13:32+01:00', 'sortable_name': 'FakeStudent, Bertil', 'short_name': 'Bertil', 'sis_user_id': 'z2', 'integration_id': None, 'sis_import_id': None, 'login_id': 's2'}}, {'id': 6, 'user_id': 5, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:15:56Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/5', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z3', 'html_url': 'http://canvas.docker/courses/4/users/5', 'user': {'id': 5, 'name': 'Cenric FakeStudent', 'created_at': '2019-01-30T15:13:33+01:00', 'sortable_name': 'FakeStudent, Cenric', 'short_name': 'Cenric', 'sis_user_id': 'z3', 'integration_id': None, 'sis_import_id': None, 'login_id': 's3'}}, {'id': 7, 'user_id': 6, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:15:57Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/6', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z4', 'html_url': 'http://canvas.docker/courses/4/users/6', 'user': {'id': 6, 'name': 'David FakeStudent', 'created_at': '2019-01-30T15:13:34+01:00', 'sortable_name': 'FakeStudent, David', 'short_name': 'David', 'sis_user_id': 'z4', 'integration_id': None, 'sis_import_id': None, 'login_id': 's4'}}, {'id': 8, 'user_id': 7, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:15:58Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': '2019-02-06T14:53:12Z', 'last_attended_at': None, 'total_activity_time': 77235, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/7', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z5', 'html_url': 'http://canvas.docker/courses/4/users/7', 'user': {'id': 7, 'name': 'Ellen FakeStudent', 'created_at': '2019-01-30T15:13:34+01:00', 'sortable_name': 'FakeStudent, Ellen', 'short_name': ' Ellen', 'sis_user_id': 'z5', 'integration_id': None, 'sis_import_id': None, 'login_id': 's5'}}, {'id': 9, 'user_id': 8, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:15:58Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/8', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z6', 'html_url': 'http://canvas.docker/courses/4/users/8', 'user': {'id': 8, 'name': 'Fran FakeStudent', 'created_at': '2019-01-30T15:13:35+01:00', 'sortable_name': 'FakeStudent, Fran', 'short_name': 'Fran', 'sis_user_id': 'z6', 'integration_id': None, 'sis_import_id': None, 'login_id': 's6'}}, {'id': 10, 'user_id': 9, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:15:59Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/9', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z7', 'html_url': 'http://canvas.docker/courses/4/users/9', 'user': {'id': 9, 'name': 'Gordon FakeStudent', 'created_at': '2019-01-30T15:13:36+01:00', 'sortable_name': 'FakeStudent, Gordon', 'short_name': 'Gordon', 'sis_user_id': 'z7', 'integration_id': None, 'sis_import_id': None, 'login_id': 's7'}}, {'id': 11, 'user_id': 10, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:15:59Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/10', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z8', 'html_url': 'http://canvas.docker/courses/4/users/10', 'user': {'id': 10, 'name': 'Håkan FakeStudent', 'created_at': '2019-01-30T15:13:37+01:00', 'sortable_name': 'FakeStudent, Håkan', 'short_name': 'Håkan', 'sis_user_id': 'z8', 'integration_id': None, 'sis_import_id': None, 'login_id': 's8'}}, {'id': 12, 'user_id': 11, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:16:00Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': None, 'last_attended_at': None, 'total_activity_time': 0, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/11', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z9', 'html_url': 'http://canvas.docker/courses/4/users/11', 'user': {'id': 11, 'name': 'Ibǘy FakeStudent', 'created_at': '2019-01-30T15:13:39+01:00', 'sortable_name': 'FakeStudent, Ibǘy', 'short_name': 'Ibǘy', 'sis_user_id': 'z9', 'integration_id': None, 'sis_import_id': None, 'login_id': 's9'}}, {'id': 13, 'user_id': 12, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-01-30T14:16:00Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': '2019-02-06T14:00:42Z', 'last_attended_at': None, 'total_activity_time': 173942, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/12', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z10', 'html_url': 'http://canvas.docker/courses/4/users/12', 'user': {'id': 12, 'name': 'James FakeStudent', 'created_at': '2019-01-30T15:13:40+01:00', 'sortable_name': 'FakeStudent, James', 'short_name': 'James', 'sis_user_id': 'z10', 'integration_id': None, 'sis_import_id': None, 'login_id': 's10'}}, {'id': 15, 'user_id': 14, 'course_id': 4, 'type': 'StudentEnrollment', 'created_at': '2019-02-06T09:18:21Z', 'updated_at': '2019-02-06T09:19:20Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': '2019-02-06T14:22:28Z', 'last_attended_at': None, 'total_activity_time': 8471, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/14', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z13', 'html_url': 'http://canvas.docker/courses/4/users/14', 'user': {'id': 14, 'name': 'Quentin FakeStudent', 'created_at': '2019-02-06T10:12:16+01:00', 'sortable_name': 'FakeStudent, Quentin', 'short_name': 'Quentin FakeStudent', 'sis_user_id': 'z13', 'integration_id': None, 'sis_import_id': None, 'login_id': 's13'}}, {'id': 14, 'user_id': 13, 'course_id': 4, 'type': 'StudentViewEnrollment', 'created_at': '2019-02-02T11:36:20Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'StudentEnrollment', 'role_id': 3, 'last_activity_at': '2019-02-03T09:47:40Z', 'last_attended_at': None, 'total_activity_time': 13288, 'sis_import_id': None, 'grades': {'html_url': 'http://canvas.docker/courses/4/grades/13', 'current_score': None, 'current_grade': None, 'final_score': None, 'final_grade': None, 'unposted_current_score': None, 'unposted_current_grade': None, 'unposted_final_score': None, 'unposted_final_grade': None}, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': None, 'html_url': 'http://canvas.docker/courses/4/users/13', 'user': {'id': 13, 'name': 'Test Student', 'created_at': '2019-02-02T12:36:19+01:00', 'sortable_name': 'Student, Test', 'short_name': 'Test Student', 'sis_user_id': None, 'integration_id': None, 'sis_import_id': None, 'login_id': '8054dc7dea06ac29b246be030ededb30a6197af0'}}, {'id': 3, 'user_id': 1, 'course_id': 4, 'type': 'TeacherEnrollment', 'created_at': '2018-12-23T17:45:34Z', 'updated_at': '2019-02-02T14:07:49Z', 'associated_user_id': None, 'start_at': None, 'end_at': None, 'course_section_id': 2, 'root_account_id': 1, 'limit_privileges_to_course_section': False, 'enrollment_state': 'active', 'role': 'TeacherEnrollment', 'role_id': 4, 'last_activity_at': '2019-02-06T19:25:13Z', 'last_attended_at': None, 'total_activity_time': 445591, 'sis_import_id': None, 'sis_account_id': None, 'sis_course_id': None, 'course_integration_id': None, 'sis_section_id': None, 'section_integration_id': None, 'sis_user_id': 'z0', 'html_url': 'http://canvas.docker/courses/4/users/1', 'user': {'id': 1, 'name': 'chip.maguire@gmail.com', 'created_at': '2018-12-12T12:08:59+01:00', 'sortable_name': 'chip.maguire@gmail.com', 'short_name': 'chip.maguire@gmail.com', 'sis_user_id': 'z0', 'integration_id': None, 'sis_import_id': None, 'login_id': 'chip.maguire@gmail.com'}}]
user name=Ann FakeStudent with id=4 and sis_id=z1
url: http://canvas.docker/api/v1/users/sis_user_id:z1/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"FakeFake","name":"Fake program","start":1600}]}}
result of getting custom data for user Ann FakeStudent is {'data': {'programs': [{'code': 'FakeFake', 'name': 'Fake program', 'start': 1600}]}}
user name=Bertil FakeStudent with id=5 and sis_id=z2
url: http://canvas.docker/api/v1/users/sis_user_id:z2/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"CDATE","name":"Degree Programme in Computer Science and Engineering","start":2016}]}}
result of getting custom data for user Bertil FakeStudent is {'data': {'programs': [{'code': 'CDATE', 'name': 'Degree Programme in Computer Science and Engineering', 'start': 2016}]}}
user name=Cenric FakeStudent with id=6 and sis_id=z3
url: http://canvas.docker/api/v1/users/sis_user_id:z3/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"CINTE","name":"Degree Programme in Information and Communication Technology","start":2016}]}}
result of getting custom data for user Cenric FakeStudent is {'data': {'programs': [{'code': 'CINTE', 'name': 'Degree Programme in Information and Communication Technology', 'start': 2016}]}}
user name=David FakeStudent with id=7 and sis_id=z4
url: http://canvas.docker/api/v1/users/sis_user_id:z4/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"CINTE","name":"Degree Programme in Information and Communication Technology","start":2016}]}}
result of getting custom data for user David FakeStudent is {'data': {'programs': [{'code': 'CINTE', 'name': 'Degree Programme in Information and Communication Technology', 'start': 2016}]}}
user name=Ellen FakeStudent with id=8 and sis_id=z5
url: http://canvas.docker/api/v1/users/sis_user_id:z5/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"CDATE","name":"Degree Programme in Computer Science and Engineering","start":2016}]}}
result of getting custom data for user Ellen FakeStudent is {'data': {'programs': [{'code': 'CDATE', 'name': 'Degree Programme in Computer Science and Engineering', 'start': 2016}]}}
user name=Fran FakeStudent with id=9 and sis_id=z6
url: http://canvas.docker/api/v1/users/sis_user_id:z6/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"TEBSM","name":"Master's Programme, Embedded Systems, 120 credits","start":2016}]}}
result of getting custom data for user Fran FakeStudent is {'data': {'programs': [{'code': 'TEBSM', 'name': "Master's Programme, Embedded Systems, 120 credits", 'start': 2016}]}}
user name=Gordon FakeStudent with id=10 and sis_id=z7
url: http://canvas.docker/api/v1/users/sis_user_id:z7/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"CDATE","name":"Degree Programme in Computer Science and Engineering","start":2016}]}}
result of getting custom data for user Gordon FakeStudent is {'data': {'programs': [{'code': 'CDATE', 'name': 'Degree Programme in Computer Science and Engineering', 'start': 2016}]}}
user name=Håkan FakeStudent with id=11 and sis_id=z8
url: http://canvas.docker/api/v1/users/sis_user_id:z8/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"TCOMM","name":"Master's Programme, Communication Systems, 120 credits","start":2016}]}}
result of getting custom data for user Håkan FakeStudent is {'data': {'programs': [{'code': 'TCOMM', 'name': "Master's Programme, Communication Systems, 120 credits", 'start': 2016}]}}
user name=Ibǘy FakeStudent with id=12 and sis_id=z9
url: http://canvas.docker/api/v1/users/sis_user_id:z9/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"CELTE","name":"Degree Programme in Electrical Engineering","start":2016}]}}
result of getting custom data for user Ibǘy FakeStudent is {'data': {'programs': [{'code': 'CELTE', 'name': 'Degree Programme in Electrical Engineering', 'start': 2016}]}}
user name=James FakeStudent with id=13 and sis_id=z10
url: http://canvas.docker/api/v1/users/sis_user_id:z10/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"TIVNM","name":"Master's Programme, ICT Innovation, 120 credits","start":2016}]}}
result of getting custom data for user James FakeStudent is {'data': {'programs': [{'code': 'TIVNM', 'name': "Master's Programme, ICT Innovation, 120 credits", 'start': 2016}]}}
user name=Quentin FakeStudent with id=15 and sis_id=z13
url: http://canvas.docker/api/v1/users/sis_user_id:z13/custom_data/program_of_study
result of getting custom data: {"message":"no data for scope"}
result of getting custom data for user Quentin FakeStudent is []
user name=Test Student with id=14 and sis_id=None
url: http://canvas.docker/api/v1/users/14/custom_data/program_of_study
result of getting custom data: {"message":"no data for scope"}
result of getting custom data for user Test Student is []
user name=chip.maguire@gmail.com with id=3 and sis_id=z0
url: http://canvas.docker/api/v1/users/sis_user_id:z0/custom_data/program_of_study
result of getting custom data: {"errors":[{"message":"The specified resource does not exist."}],"error_report_id":642}
result of getting custom data for user chip.maguire@gmail.com is []
url: http://canvas.docker/api/v1/users/self/custom_data/program_of_study
result of getting custom data: {"data":{"programs":[{"code":"FakeFake","name":"Fake program","start":1600}]}}
result of getting custom data for user self is {'data': {'programs': [{'code': 'FakeFake', 'name': 'Fake program', 'start': 1600}]}}
```

## list-external-tools-for-course.py

Purpose: To external tools for a Canvas course

Input:
```
list-external-tool-for-course.py  course_id tool_id 'navigation_text'

```

Output: a list of external tools for the given course_id

Example:
With the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
With the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program

list-external-tools-for-course.py -C 5

Can also be called with an alternative configuration file:
list-external-tools-for-course.py --config config-test.json 4

list-external-tools-for-course.py 4
```



## add-external-tool-for-course.py
Purpose: To add an external to to a Canvas course

Input:
```
add-external-tool-for-course.py  course_id tool_id 'navigation_text'

```

Output: a list of external tools for the given course_id

Example:
With the option '-C'or '--containers' use HTTP rather than HTTPS for access to Canvas
With the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program

add-external-tool-for-course.py 4 2 'TestTool'

Can also be called with an alternative configuration file:
add-external-tool-for-course.py --config config-test.json 4 2 'TestTool'

add-external-tool-for-course.py -C 5 2 'TestTool'
```

## list_calendar_events.py

Purpose: To output calendar events into an XLSX file

Input:
```
./list_calendar_events.py user_id
```

Output: outputs a file with a name of the form: calendar-user_id.xlsx

## create_calendar_event.py

Purpose: To be able to experiment with creating calendar events.

Input:
```
./create_calendar_event.py user_id date title description
```

Output: Nothing

Note: Can be modified to use a course or a user content.

## list_calendar_events.py

Purpose: Create a spreadsheet of a user's calendar events

Input:
```
./list_calendar_events.py user_id
```

Output: XLSX spreadsheet of the user's calendar events. The format of the file name is: calendar-user_id.xlsx

## custom-columns-in-course.py

Purpose: To output all of the customn columns in a course as a spreadsheet

Input:
```
./custom-columns-in-course.py course_id
```

Output: A XLSX spreadsheet with all of the information from the custom columns in a given course.

## insert-custom-columns-from-spreadsheet.py

Purpose: To enter data into the names customn columns in a course from a spreadsheet

Input:
```.
insert-custom-columns-from-spreadsheet.py  course_id column_name_1 column_name_2 ...
```

Output: Updates the gradebook

## add-columns-for-II2202-final-presentation.py
Purpose: To create custom columns in the gradebook to make it easier for each teacher to take notes during the final presentation (avoiding the user of a spreadsheet).

Input:
```
add-columns-for-II2202-final-presentation.py  course_id start_date end_date
```

Output: Adds the columns to the course's gradebook and populates the "Opponents" columns with the name of the student's peer reviwer and populates the "Oral presentation date/time" columns with the date and time of the oral presentation as scheduled in the calendar.

Note: The columns are custom columns that can have up to ~256 characters entered into them. This is a limitation of the custom columns due to their underlying representation in the database used by Canvas.

Example:
```
For II2202 P1 the assignment to use to learn who the opponents are is set as follows
        opposition_assignment_name="Opposition before final seminar"
then the program is run as:
./add-columns-for-II2202-final-presentation.py 6434 2019-01-01 2019-02-01
```

## insert-group_column_in_gradebook.py

Purpose: Inserts a custom column with the indicated name using the data from
from the named groupset (it will create the column as necessary).  Note that
one can optionally strip a fixed prefix from the group names. For example, if
each group name begins with "Project group" followed by space and a number
then
   ./insert-group_column_in_gradebook.py 6433 New_groups "Project Groups" "Project group"
will simply insert the number with the leading space stripped.

Input:
```
./insert-group_column_in_gradebook.py  course_id column_name groupset_name [prefix_to_remove]
```

Output: No ouput unless run in verbose mode.

Example:
 ./insert-group_column_in_gradebook.py 6433 New_groups "Project Groups"

 ./insert-group_column_in_gradebook.py 6433 New_groups "Project Groups" "Project group"

## insert_grades_and_comments.py

Purpose: Inserts grades for an assignment into the gradebook for a course.
	 The column headings of the gradebook are assumed to have the form (where dddd is a user_id):
	   Student,ID,assignment_name,assignment_name*comment*
	   xxxx,dddd,A,"I wish I had written this report"
	   xxxx,dddd,E,"Terrible report"

Input:
```
./insert_grades_and_comments.py course_id assignment_id file.csv
```

Output: No ouput unless run in verbose mode.

Example:
./insert_grades_and_comments_indirect.py 6433 25425 inser_grades_and_comments_test.csv

## insert_grades_and_comments_indirect.py

Purpose: Inserts grades for an assignment into the gradebook for a course.
	 The column headings of the gradebook are assumed to have the form (where dddd is a pseudo user_id):
	   Student,ID,assignment_name,assignment_name*comment*
	   xxxx,dddd,A,"I wish I had written this report"
	   xxxx,dddd,E,"Terrible report"

Input:
```
./insert_grades_and_comments_indirect.py course_id assignment_id file.csv indirect_column_name
```

Output: No ouput unless run in verbose mode.

Example:
./insert_grades_and_comments_indirect.py 6433 25425 inser_grades_and_comments_test.csv "New_groups"

## students-in-my-courses.py

Purpose: To create a spreadsheet of all students in my own courses to be able to look up which courses a student has been in.

Input:
```
./students-in-my-courses.py
```

Output: spreadsheet with a page per course in a file named "users_in_my_courses.xlsx"

Note: It skips courses involving the whole of KTH (as of 2019-08-15)

## students-in-my-courses-with-cat.py

Purpose: To create a spreadsheet of all students in my own courses to be able to look up which courses a student has been in.

Input:
```
./students-in-my-courses-with-cat.py
```

Output: spreadsheet with a page per course in a file named "users_in_my_courses.xlsx"

Note: It skips courses involving the whole of KTH (as of 2019-08-15). Note also that it computes a sheet called "concat" that contains the concatinated data from the separate spreadsheets.


## students-in-my-courses-with-join.py

Purpose: To create a spreadsheet of all students in my own courses to be able to look up which courses a student has been in.

Input:
```
./students-in-my-courses-with-join.py
```

Output: spreadsheet with a page per course in a file named "users_in_my_courses.xlsx"

Note: It skips courses involving the whole of KTH (as of 2019-08-15). Note also that it computes a sheet called "Summary" that contains a summary of all of the information about the students and which courses they were in. This page has all of the students, the individual courses (by course_id), and a list of all courses (by course_id) the student was in.

Further note that it does not acutal use a join operation, but actually computes two dictionaries: one with information about the student (user_id, login ID, SIS_user_id, and various forms of the user's name) and the other with the list of course that a give user has been a student in. These data structures are then turned into a Python Pandas DataFrame and then output as the summary sheet. [However, logically the operation is a join on the data based on the user information.]


## copy-peer-reviewer-assignments.py

Purpose: To copy peer reviewing assignments from one assignment to another

Input:
```
./copy-peer-reviewer-assignments.py course_id old_assignment_id new_assignment_id
```

Output: outputs information about the assigned peer review of the form:
   result of post assigning peer reviwer: {"id":xxx,"user_id":yyy,"asset_id":zzz,"asset_type":"Submission","workflow_state":"assigned","assessor_id":qqqq}


Example:
```
./copy-peer-reviewer-assignments.py 12162 86839 86851
```

In the above case the old_assignment was 86839 and the new assignment was 86851.

## list-peer_reviewing_assignments.py

Purpose: To have a summary of who is the peer reviewer for whom

Input:
```
./list-peer_reviewing_assignments.py course_id assignment_id
```

Output: outputs a summary of peer reviewing assignments as an xlsx file of the form: peer_reviewing_assignments-189.xlsx

Note 

Example:
```
./list-peer_reviewing_assignments.py 12162 86851
```


## update-custom-column.py

Purpose: To change the name/title of a custom column

Input:
```
./update-custom-column.py  course_id column_id column_name
```

Example:
```
./update-custom-column.py -v 12162 1205 "Grade for oral opposition"
```

## list-features-for-course.py

Purpose: To list the features for a course

Input:
```
./list-features-for-course.py  course_id
```

Output: outputs the features as a vector


Example:
```
./list-features-for-course.py  19885
[{'applies_to': 'Course',
  'description': 'Learning Mastery Gradebook provides a way for teachers to '
                 'quickly view student and course\n'
                 'progress on course learning outcomes. Outcomes are presented '
                 'in a Gradebook-like\n'
                 'format and student progress is displayed both as a numerical '
                 'score and as mastered/near\n'
                 'mastery/remedial.',
  'display_name': 'Learning Mastery Gradebook',
  'feature': 'outcome_gradebook',
  'feature_flag': {'context_id': 19885,
                   'context_type': 'Course',
                   'feature': 'outcome_gradebook',
                   'locked': False,
                   'locking_account_id': None,
                   'state': 'on',
                   'transitions': {'off': {'locked': False}}},
  'root_opt_in': False},
 {'applies_to': 'Course',
  'description': 'Create assessments with New Quizzes and migrate existing '
                 'Canvas Quizzes.',
  'display_name': 'New Quizzes',
  'feature': 'quizzes_next',
  'feature_flag': {'context_id': 1,
                   'context_type': 'Account',
                   'feature': 'quizzes_next',
                   'locked': True,
                   'locking_account_id': None,
                   'state': 'on',
                   'transitions': {'off': {'locked': False}}}},
 {'applies_to': 'Course',
  'description': 'Prevents students from leaving annotations in assignments. '
                 'Does not apply to peer-reviewed assignments.',
  'display_name': 'Restrict Students from Annotating',
  'feature': 'restrict_students_from_annotating',
  'feature_flag': {'feature': 'restrict_students_from_annotating',
                   'locked': False,
                   'state': 'allowed',
                   'transitions': {'off': {'locked': False},
                                   'on': {'locked': False}}}},
 {'applies_to': 'Course',
  'description': 'Allow switching to the enhanced RCE',
  'display_name': 'RCE Enhancements',
  'feature': 'rce_enhancements',
  'feature_flag': {'context_id': 170000000000002,
                   'context_type': 'Account',
                   'feature': 'rce_enhancements',
                   'locked': True,
                   'locking_account_id': None,
                   'state': 'off',
                   'transitions': {'on': {'locked': False}}},
  'root_opt_in': True},
 {'applies_to': 'Course',
  'description': 'Show new analytics for course and user data',
  'display_name': 'New Course and User Analytics',
  'feature': 'analytics_2',
  'feature_flag': {'context_id': 19885,
                   'context_type': 'Course',
                   'feature': 'analytics_2',
                   'locked': False,
                   'locking_account_id': None,
                   'state': 'on',
                   'transitions': {'off': {'locked': False}}}},
 {'applies_to': 'Course',
  'description': 'Enable the tracking of events for a quiz submission, and the '
                 'ability\n'
                 '      to view a log of those events once a submission is '
                 'made.',
  'display_name': 'Quiz Log Auditing',
  'feature': 'quiz_log_auditing',
  'feature_flag': {'feature': 'quiz_log_auditing',
                   'locked': False,
                   'state': 'allowed',
                   'transitions': {'off': {'locked': False},
                                   'on': {'locked': False}}}},
 {'applies_to': 'Course',
  'description': 'Enable anonymous grading of assignments.',
  'display_name': 'Anonymous Grading',
  'feature': 'anonymous_marking',
  'feature_flag': {'context_id': 1,
                   'context_type': 'Account',
                   'feature': 'anonymous_marking',
                   'locked': False,
                   'locking_account_id': None,
                   'state': 'allowed',
                   'transitions': {'off': {'locked': False},
                                   'on': {'locked': False}}},
  'root_opt_in': True},
 {'applies_to': 'Course',
  'description': 'Enable moderated grading.',
  'display_name': 'Moderated Grading',
  'feature': 'moderated_grading',
  'feature_flag': {'context_id': 1,
                   'context_type': 'Account',
                   'feature': 'moderated_grading',
                   'locked': False,
                   'locking_account_id': None,
                   'state': 'allowed',
                   'transitions': {'off': {'locked': False},
                                   'on': {'locked': False}}},
  'root_opt_in': True},
 {'applies_to': 'Course',
  'description': 'Student Learning Mastery Gradebook provides a way for '
                 'students to quickly view progress\n'
                 'on course learning outcomes. Outcomes are presented in a '
                 'Gradebook-like\n'
                 'format and progress is displayed both as a numerical score '
                 'and as mastered/near\n'
                 'mastery/remedial.',
  'display_name': 'Student Learning Mastery Gradebook',
  'feature': 'student_outcome_gradebook',
  'feature_flag': {'context_id': 19885,
                   'context_type': 'Course',
                   'feature': 'student_outcome_gradebook',
                   'locked': False,
                   'locking_account_id': None,
                   'state': 'on',
                   'transitions': {'off': {'locked': False}}},
  'root_opt_in': False},
 {'applies_to': 'Course',
  'description': 'Anonymize all instructor comments and annotations within '
                 'DocViewer',
  'display_name': 'Anonymous Instructor Annotations',
  'feature': 'anonymous_instructor_annotations',
  'feature_flag': {'feature': 'anonymous_instructor_annotations',
                   'locked': False,
                   'state': 'allowed',
                   'transitions': {'off': {'locked': False},
                                   'on': {'locked': False}}},
  'root_opt_in': False},
 {'applies_to': 'Course',
  'description': 'New Gradebook enables an early release of new Gradebook '
                 'enhancements.',
  'display_name': 'New Gradebook',
  'feature': 'new_gradebook',
  'feature_flag': {'context_id': 19885,
                   'context_type': 'Course',
                   'feature': 'new_gradebook',
                   'locked': False,
                   'locking_account_id': None,
                   'state': 'on',
                   'transitions': {'off': {'locked': False}}},
  'root_opt_in': True},
 {'applies_to': 'Course',
  'description': 'Allows the duplication of Calendar Events',
  'display_name': 'Duplicating Calendar Events',
  'feature': 'recurring_calendar_events',
  'feature_flag': {'context_id': 170000000000002,
                   'context_type': 'Account',
                   'feature': 'recurring_calendar_events',
                   'locked': True,
                   'locking_account_id': None,
                   'state': 'on',
                   'transitions': {'off': {'locked': False}}},
  'root_opt_in': True},
 {'applies_to': 'Course',
  'description': 'List students by their sortable names in the Gradebook. '
                 "Sortable name defaults to 'Last Name, First Name' and can be "
                 'changed in settings.',
  'display_name': 'Gradebook - List Students by Sortable Name',
  'feature': 'gradebook_list_students_by_sortable_name',
  'feature_flag': {'feature': 'gradebook_list_students_by_sortable_name',
                   'locked': False,
                   'state': 'allowed',
                   'transitions': {'off': {'locked': False},
                                   'on': {'locked': False}}}}]

```

## set-features-for-course.py

Purpose: To set a specific features for a course to a given state

Input:
```
./set-features-for-course.py  course_id feature state
```

Output: outputs the resulting feature

Example:
```
./set-features-for-course.py -v 19885 outcome_gradebook off
{'context_id': 19885,
 'context_type': 'Course',
 'feature': 'outcome_gradebook',
 'locked': False,
 'locking_account_id': None,
 'state': 'off',
 'transitions': {'on': {'locked': False}}}
```
Another example:
```
./set-features-for-course.py -v 19885 outcome_gradebook on
{'context_id': 19885,
 'context_type': 'Course',
 'feature': 'outcome_gradebook',
 'locked': False,
 'locking_account_id': None,
 'state': 'on',
 'transitions': {'off': {'locked': False}}}
 ```

## list_sections_in_course.py
Purpose: To output a spreadsheet of the sections in a course and the students in these sections

Input:
```
./list_sections_in_course.py course_if
```

Output: outputs a file with a name of the form: sections-in-{course_id}.xlsx

Example:
```
./list_sections_in_course.py 19885
```

Note:  If there are no sections, this page is  not included in the spreadsheet. 
       If there are no students this page is not included in the spreadsheet. 


## /create_JSON_file_of_sections_in_your_courses.py
Purpose:
  Create a JSON file with information about courses where user enrolled as a 'TeacherEnrollment', 'Examiner', or 'TaEnrollment'

The JSON file contains a course_info dict 
   courses_to_ignore=course_info['courses_to_ignore'] - courses that the user wants to ignore
   courses_without_specific_sections=course_info['courses_without_specific_sections'] - courses where the user is responsible for all the students
   courses_with_sections=course_info['courses_with_sections']  - courses where the user has a specific section
               the specific section's name may be the user's name or some other unique string (such as "Chip's section")
               Because the name of the relevant section can be arbitrary, this file is necessary to know which section belongs to a given user
 
Input:
```
./create_JSON_file_of_sections_in_your_courses.py [-v] [--config config.json] [-s course_info.json] [-U] [-X]
```

With the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program

Can also be called with an alternative configuration file:
 ./create_JSON_file_of_sections_in_your_courses --config config-test.json

Examples:
```
   create file for only exjobb courses:
      ./create_JSON_file_of_sections_in_your_courses.py -s fee.json -X

   update an existing file (possibly adding new courses)
      ./create_JSON_file_of_sections_in_your_courses.py -s foo.json -U
```

## list_ungraded_submissions_in_your_courses_JSON.py

Purpose: output a list of ungraded assignments for a user to grade

Input:
```
./list_ungraded_submissions_in_your_courses_JSON.py [-v] [--config config.json] [-s course_info.json] [-t] [-X]
```

With the option "-v" or "--verbose" you get lots of output - showing in detail the operations of the program

With the option "-t" or "--testing" only does a specific set of courses ids (built into the program)

With the option "-X" of "--exjobs" only processes degree project courses

The JSON file contains a course_info dict 
   courses_to_ignore=course_info['courses_to_ignore'] - courses that the user wants to ignore
   courses_without_specific_sections=course_info['courses_without_specific_sections'] - courses where the user is responsible for all the students
   courses_with_sections=course_info['courses_with_sections']  - courses where the user has a specific section
               the specific section's name may be the user's name or some other unique string (such as "Chip's section")
               Because the name of the relevant section can be arbitrary, this file is necessary to know which section belongs to a given user

Can also be called with an alternative configuration file:
 ./create_JSON_file_of_sections_in_your_courses --config config-test.json

Examples:
```
./list_ungraded_submissions_in_your_courses_JSON.py -t
```

## modules-items-in-course-json.py

Purpose: To extract the modules and page information for a course in JSON

Input:
```
./modules-items-in-course-json.py course_id
```

Output: outputs a JSON file with a name of the form: "modules-in-course-course_id.json"

Example:
```
./modules-items-in-course.py 11

./modules-items-in-course.py --config config-test.json 11

```


## compute_stats_for_pages_in_course.py

Purpose: To computer some readability statistics for each page in a course

Input:
```
./compute_stats_for_pages_in_course.py  course_id

```

Output: outputs an XLSX formatted file with a name of the form: 'statistics-for-course-'+str(course_id)+'.xlsx
	The statistics are computed using Textatistic (see http://www.erinhengel.com/software/textatistic/)

Example:
```
./compute_stats_for_pages_in_course.py 11

./compute_stats_for_pages_in_course.py --config config-test.json 11

```

## cgetall.py

Purpose: To get all of the pages from a Canvas course as local files

Input:
```
./cgetall.py  canvas_course_page_url|course_id [destination_directory]

```

Output: outputs each page as a file with the extenssion ".html" the basename is taken from the title of the page

Example:
```
cgetall.py https://kth.instructure.com/courses/11/pages/test-3

cgetall.py 11

```


## modules-items-in-course-json.py

Purpose: To collect information about all of the modules in a course

Input:
```
./modules-items-in-course-json.py course_id
```

Output: outputs a JSON file with the information about each of the modules in the course and each of the module items in a given module
	The file name isof the form: modules-in-course-xxxx.json where xxxx is the course_id

Example:
```
./modules-items-in-course.py 11

./modules-items-in-course.py 17234
```

## find_keyords_phrase_in_files.py

Purpose: To extract from a directory of files of the pages from a course words or phrases

Input:
```
./find_keyords_phrase_in_files.py direcory
```

Output: outputs a file with a name of the form keywords_and_phrases_xx.json from the *-html files in the directory

Note the files are placed in the directory by using cgetall.py course_id

Example:
```
./find_keyords_phrase_in_files.py /tmp/testdik1552
```

## create_page_from_json.py

Purpose: To create the contents for a page with information about each language with the words used and URLs to their usage

Input:
```
./create_page_from_json.py course_id input.json
```

Output: outputs a file with a name of the form stats_for_course-xxxx.html where xxxx is the course_id

Example:
```
./create_page_from_json.py 17234 keywords_and_phrases_testdik1552.json
```

## Making an index

Purpose: To create an index for a Canvas course

Input:
```
# Create a directory to put all the pages for the course
mkdir  /tmp/testdik1552

# Get all the pages for the course_id 17234
./cgetall.py 17234 /tmp/testdik1552

# Get information about the modules in this course
./modules-items-in-course.py 17234
# the above creates the file: modules-in-course-17234.json

# Fine the keywords and phases in the files in the indicated directory
./find_keyords_phrase_in_files.py -r /tmp/testdik1552
# the above create the file: keywords_and_phrases_testdik1552.json
# The "-r" option causes the program to ignore everything after a horizontal rules <hr> or </ hr>

# Create an index
./create_page_from_json.py 17234 keywords_and_phrases_testdik1552.json
 the above creates the file: stats_for_course-17234.html

# Copy (or rename) the file, so that it has a name suitable for an Canvas page
cp stats_for_course-17234.html test-page-3.html

# Upload the created page and give it a title, in this case "Test page 3"
./ccreate.py https://xxxx.instructure.com/courses/17234/pages/test-page-3 "Test page 3"

# Put the page into a module in the course by going to a module, clicking the plus symbol
# then select the type of module to add as "Page" and then select the item in the scrolling list "Test page 3"
# Note that you need to refresh the "Modules" page to be able to see the new choice of page.

# Note that if your use the ccreate.py script multiple times, the page will have names of the form: "Test page 3-i", such as "Test page 3-6". 

# You can eliminate the uploaded page by using the page: https://xxxx.instructure.com/courses/17234/pages
# Click on the three vertical dots on the right and select "Delete"

# You can eliminate the page from the module using the three dots on the right and select "Remove"

```

Output: Outputs a web page with various indexes. 

You can iterate creating the index and uploading to optimize what is indexed and how it is indexed. When you edit the HTML files in /tmp/testdik1552 - remember to update the actual web page in the Canvas course. A convenient way to do this is to edit the course page and select the HTML view and paste in the contents of the edited HTML file.

Once you have completed the editing, start the procedure above with the step: find_keyords_phrase_in_files.py
Otherwise your changes will not be correctly processed.

Some of the changes that I have made to the HTML is to tag words that I want to be kep together (such as a person's name or a logical concept):
	<span>Adam Smith</span>
	<span>Autonomous system number</span>	

Similarly, you can mark text that you do not want to be indexed:
	<span class="dont-index">20% error rate</span>

Similarly, you can mark text that you do not want to be indexed because it is a reference to the literature (I find that this is commonly necessary because I have put a references into a figcaption of caption OR because I have added a reference in-line in the page, rather than following the horizontal rule):
	<span class="inline-ref">(see Smith, Figure 10, on page 99.)</span>

Note that the rules for what text to index and what text to ignore are rather
*ad hoc* and hard coded into the program (find_keyords_phrase_in_files.py and
create_page_from_json.py). However, one can change the source code to tune it
as you want. For example, one of the things that I chose to not index is all
superscripts and subscripts (i.e., <sup>xxxx</sup> and <sub>xxxx</sub>). I
also exclude alt text for images that begins with 'LaTeX:' - in order to
eliminate the LaTeX for equations.

The logical separation between find_keyords_phrase_in_files.py and
create_page_from_json.py is that the first computes a list of "strings" for each
tag of each HTML pages, producing a dictionary with the HTML file name as key and entries of the form:

"sctp-header.html":
	{"list_item_text": ["As with UDP & TCP, SCTP provides de/multiplexing via the 16-bit source and destination ports.", "Associations between endpoints are defined by a unique ", "SCTP applies a CRC-32 end-to-end checksum to its general header and all the chunks", "Control information is contained in Control Chunks (these always ", "Multiple data chunks can be present - each containing data for different streams"],
          "paragraph_text": ["16-bit source port", "16-bit source port", "12 bytes", "32-bit verification tag", "32-bit Checksum", "Control chunk(s) {If any}", "Data chunk(s) {If any}", "SCTP packet (see ", "IP protocol x84 = SCTP", "A separate verification tag is used in each direction", "(Previously it used Adler-32 checksum [RFC 3309])"],
	 "strong_text": ["General Header", "verification tag", "Chunks", "precede "]
	 },

 While the later program constructs the index page. I found that I had to tune the strings in list starting_characters_to_remove and in the list ending_characters_to_remove to get the results that I wanted. One of the artifacts of cutting and pasting from PowerPoint slides to create the Canvas pages was that some of the characters that appear are Unicode characters for different dashes and some symbols that I have used (such as u'→', u'⇒', u'⇨', u'∴', u'≡', u'✔', u'❌') and generally I do not want to have these indexed (but rather treat them like stop words).

Overall, the process of generating an index was useful - as I found mis-spellings, inconsistent use of various terms and capitalization, random characters that seemed to have been typos or poor alternative img descriptions, ...). However, it remains a work in progress.

<!-- 

## xxx.py

Purpose: To 

Input:
```
./xxx.py KTHID_of_user
```

Output: outputs 

Note 

Example:
```
./xxx.py u1d13i2c
```

You can xxxx, for example:
```

```

## yyy.py

Purpose: To 

Input:
```
./xxx.py KTHID_of_user
```

Output: outputs 

Note 

Example:
```
./xxx.py u1d13i2c
```

You can xxxx, for example:
```

```

-->

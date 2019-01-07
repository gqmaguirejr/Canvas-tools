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
./list_your_courses_JSON.py
```

Output: outputs JSON for user's courses

Example (edited to show only some of the output):
```
./list_your_courses_JSON.py
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
./list_your_courses.py
```

Output: outputs a file (courses-self.xlsx) containing a spreadsheet of the user's courses

```
./list_your_courses.py
```

## users-in-course.py

Purpose: To get a list of the users in a course together with their sections and avatars

Input:
```
./users-in-course.py course_id
```

Output: XLSX spreadsheet with textual section names and URL to user's avatar

Note that getting the avatars takes some time, hence this is optional

Examples:
```
./users-in-course.py --config config-test.json 6434

./users-in-course.py --config config-test.json --avatar 6434

 ./users-in-course.py --config config-test.json --avatar -p 11

To make images 90x90 pixels in size:
 ./users-in-course.py --config config-test.json --avatar -p -s 90 11
```

## modules-in-course.py

Purpose: To list the modules in a course in a spreadsheet

Input: course_id
```
./modules-in-course.py course_id
```

Output: outputs a spreadsheet named 'modules-'+course_id+'.xlsx'

Example:
```
./modules-in-course.py 11

./modules-in-course.py --config config-test.json 11
```

## modules-items-in-course.py
Purpose: To list the module items in a course in a spreadsheet

Input: course_id
```
./module-items-in-course.py course_id
```

Output: outputs a spreadsheet named 'module-items-'+course_id+'.xlsx'

Example:
```
./module-items-in-course.py 11

./module-items-in-course.py --config config-test.json 11
```

## assignments-in-course.py

Purpose: To list the assignments in a course in a spreadsheet

Input: course_id
```
./assignments-in-course.py course_id
```

Output: outputs a spreadsheet named 'assignments-'+course_id+'.xlsx'

Example:
```
./assignments-in-course.py 11

./assignments-in-course.py --config config-test.json 11
```

## quizzes-in-course.py

Purpose: To list the quizzes in a course in a spreadsheet

Input: course_id
```
./quizzes-in-course.py course_id
```

Output: outputs a spreadsheet named 'quizzes-'+course_id+'.xlsx'

Example:
```
./quizzes-in-course.py 11

./quizzes-in-course.py --config config-test.json 11
```

## custom-columns-in-course.py

Purpose: To list the custom columns in a spreadsheet

Input:
```
./custom-columns-in-course.py course_id
```

Example:
```
./custom-columns-in-course.py 1585
```

## delete-custom-columns-in-course.py

Purpose: To delete a custom column or all custom columns from a course

Input:
```
To delete a specific custom column:
  ./delete-custom-columns-in-course.py course_id column_id

To delete aall custom column:
  ./delete-custom-columns-in-course.py -a course_id

```

Example:
```
Delete one column:
   ./delete-custom-columns-in-course.py 12683 1118
Delete all columns:
  ./delete-custom-columns-in-course.py -v --config config-test.json -a 12683
```


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




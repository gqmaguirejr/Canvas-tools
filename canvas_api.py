#!/usr/bin/python3

# This code is directly derived from Maguire's functions in Canvas-tools.
# The functions have been refactored and simplified into this API handler.
# Johan Berg 2022-04-11

from requests import Session, codes # pip install requests

DEFAULT_TIMEOUT = 10

class CanvasAPI:
    """Handler for setup and fetching common endpoints at the Canvas API."""

    def __init__(self, config: dict, verbose: bool = False) -> None:
        try:
            # Take out the config variables used to access Canvas API via HTTP requests
            self.base_url = f'https://{config["canvas"]["host"]}/api/v1'
            access_token = config["canvas"]["access_token"]
            header = {'Authorization': f'Bearer {access_token}'}
        except KeyError as e:
            print('Missing keys in config file')
            raise e

        # Set the Authorization header for all requests in this session
        self.session = Session()
        self.session.headers.update(header)

        self.verbose = verbose

    def verbose_print(self, *args, **kwargs):
        if self.verbose:
            print(*args, **kwargs)

    def paginated_response(self, url: str, **kwargs) -> list:
        # the following is needed when the reponse has been paginated
        # i.e., when the response is split into pieces - each returning only some of the list
        # see "Handling Pagination" - Discussion created by tyler.clair@usu.edu on Apr 27, 2015, https://community.canvaslms.com/thread/1500
        pages = []
        while url:
            with self.session.get(url, **kwargs) as r:
                self.verbose_print(f'result from a paginated response: {r.text}')
                if r.status_code != codes.ok:
                    break
                pages.append(r.json())
            url = r.links.get('next', {}).get('url', '')
        return pages

    def get_course_info(self, course_id) -> dict:
        """
        Get the course info.
        `GET /api/v1/courses/:course_id`
        """
        url = f'{self.base_url}/courses/{course_id}'
        self.verbose_print(f'course info url: {url}')
        with self.session.get(url, timeout=DEFAULT_TIMEOUT) as r:
            self.verbose_print(f'result of getting course info: {r.text}')
            if r.status_code != codes.ok:
                return None
            return r.json()

    def list_quizzes(self, course_id) -> list:
        """
        Get the list of quizzes for the course.
        `GET /api/v1/courses/:course_id/quizzes`
        """
        url = f'{self.base_url}/courses/{course_id}/quizzes'
        self.verbose_print(f'list quizzes url: {url}')
        extra_parameters = {'per_page': '100'}
        pages = self.paginated_response(url, params=extra_parameters, timeout=DEFAULT_TIMEOUT)
        return [item for page in pages for item in page]

    def list_quiz_questions(self, course_id, quiz_id) -> list:
        """
        Get the list of questions for a quiz in the course.
        `GET /api/v1/courses/:course_id/quizzes/:quiz_id/questions`
        """
        url = f'{self.base_url}/courses/{course_id}/quizzes/{quiz_id}/questions'
        self.verbose_print(f'list quiz questions url: {url}')
        extra_parameters = {'per_page': '100'}
        pages = self.paginated_response(url, params=extra_parameters, timeout=DEFAULT_TIMEOUT)
        return [item for page in pages for item in page]

    def list_quiz_submissions(self, course_id, quiz_id):
        """
        Get all quiz submissions.
        `GET /api/v1/courses/:course_id/quizzes/:quiz_id/submissions`
        Parameter | Type   | Description
        --------- | ------ | -----------
        include[] | string | Associations to include with the quiz submission. Allowed values: submission, quiz, user
        """
        url = f'{self.base_url}/courses/{course_id}/quizzes/{quiz_id}/submissions'
        self.verbose_print(f'list quiz questions url: {url}')
        extra_parameters = {'per_page': '100', 'include[]': 'submission'}
        pages = self.paginated_response(url, params=extra_parameters, timeout=DEFAULT_TIMEOUT)
        return [item for page in pages for item in page.get('quiz_submissions', [])]

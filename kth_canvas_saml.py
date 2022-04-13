#!/usr/bin/python3

"""
Toolkit for signing in to KTH's Canvas LMS (through SAML) directly in Python.
This allows you to make scripts that access login-protected pages.
This extends the range of possibilities beyond what the Canvas LMS API offers,
allowing the user to automate even more tasks involving Canvas.

Example usage:
```py
>>> from kth_canvas_saml import kth_canvas_login
>>> s = kth_canvas_login('<user>@ug.kth.se', '<password>')
>>> r = s.get('https://canvas.kth.se/courses/<course_id>/quizzes/<quiz_id>/history?quiz_submission_id=<subm_id>&version=1')
>>> print(r.text)
```

Running this script alone will prompt you for credentials and test the sign in with verbose printouts:
```text
$ ./kth_canvas_saml.py
Testing KTH Canvas login.
KTH username: test
Password for user test@ug.kth.se:
Got response from https://canvas.kth.se/login : code 302
Got response from https://canvas.kth.se/login/saml : code 302
... [rest of output hidden]
```

Remember to handle your password with care!
If you do not wish to have your password stored in plain text,
you may use `kth_canvas_login_prompt`, or make something yourself.

The two dependencies can be installed with: `pip install requests beautifulsoup4`


Author: Johan Berg, 2022-04-09
"""

from urllib.parse import urljoin
from getpass import getpass

# The requests library for keeping state between HTTP requests
from requests import Request, Response, Session, codes # pip install requests

# Beautiful Soup for parsing HTML
from bs4 import BeautifulSoup # pip install beautifulsoup4


KTH_CANVAS_LOGIN = 'https://canvas.kth.se/login'
KTH_EMAIL_SUFFIX = '@ug.kth.se'
DEFAULT_TIMEOUT = 10


def kth_canvas_login_prompt(user: str = '', password: str = '', **kwargs) -> Session:
    """Prompt for username and password if not provided, then send them and kwargs to `kth_canvas_login`."""
    user = user or input('KTH username: ')
    if '@' not in user:
        user += KTH_EMAIL_SUFFIX
    password = password or getpass(f'Password for user {user}: ')
    return kth_canvas_login(user, password, **kwargs)


def kth_canvas_login(
        user: str,
        password: str,
        login_url: str = KTH_CANVAS_LOGIN,
        session: Session = None,
        timeout: float = DEFAULT_TIMEOUT,
        verbose: bool = False,
        ) -> Session:
    """
    Goes through the chain of redirects and logs in to Canvas with the provided credentials,
    returning a `Session` with the proper cookies needed to access Canvas pages.

    Parameters:
      `user`: Email address of user.
      `password`: The password.
      `login_url`: A starting point that redirects to the sign in process.
      `session`: If a session is provided, the requests will continue from there, otherwise creates a new one.
      `timeout`: Max number of seconds to wait for each response.
      `verbose`: If True, print more information.

    Returns:
      `Session` with cookies allowing access to Canvas pages.

    Raises:
      `ValueError`: When the login fails.
    """
    if verbose and not user.endswith(KTH_EMAIL_SUFFIX):
        print(f'Warning, username {user} seems to be invalid')

    # Use the provided session or create a new one
    s = session or Session()

    if verbose:
        # Add callback printouts in verbose mode
        s.hooks['response'].append(lambda r, *a, **kw: print(f'Got response from {r.url} : code {r.status_code}'))
        print(f'Authenticating at {login_url}')

    # Try to access Canvas, get redirected to KTH SAML
    r = s.get(login_url, timeout=timeout)
    verify_ok(r)

    # Send in first form, continue to KTH login
    req = html_form_to_request(r.text, r.url, {'name': 'form1', 'method': 'post', 'action': True})
    r = s.send(s.prepare_request(req), timeout=timeout)
    verify_ok(r)

    # Send KTH login credentials
    req = html_form_to_request(r.text, r.url, {'id': 'loginForm', 'method': 'post', 'action': True})
    req.data['UserName'] = user
    req.data['Password'] = password
    r = s.send(s.prepare_request(req), timeout=timeout)
    verify_ok(r)
    # Assumes a correct login causes a 302 redirect, therefore raising the error if we were not redirected here.
    # (A very naive check for login validity)
    if not r.history:
        raise ValueError('Sign in failed. Incorrect credentials?')

    # Send SAML token back to KTH SAML
    req = html_form_to_request(r.text, r.url, {'name': 'hiddenform', 'method': 'POST', 'action': True})
    r = s.send(s.prepare_request(req), timeout=timeout)
    verify_ok(r)

    # Send SAML token back to Canvas
    req = html_form_to_request(r.text, r.url, {'method': 'post', 'action': True})
    r = s.send(s.prepare_request(req), timeout=timeout)
    verify_ok(r)

    if verbose:
        print('Authentication successful')

    # Session should now contain a valid Canvas session cookie
    return s


def html_form_to_request(html: str, url: str, attributes: dict = {}, default_input_value: str = 'false') -> Request:
    """
    Parses HTML to find a <form> element and constructs a `Request` that
    contains (roughly) the POST request that a browser would send if the form was submitted.
    If multiple forms match, the first one is used.

    Parameters:
      `html`: String of HTML to parse.
      `url`: URL where the HTML was fetched from. This is to calculate the resulting requests' destination.
      `attributes`: Dict where keys are names of attributes the form must have, and values are "filters",
                    see https://beautiful-soup-4.readthedocs.io/en/latest/#kinds-of-filters .
      `default_input_value`: This value is used when an <input> does not have a 'value' field.

    Returns:
      A `Request` that can be prepared with or without a `Session`, and then sent.

    Raises:
      `ValueError`: If no matching form was found.
    """
    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')

    # Find the first <form> element with the correct attributes.
    # Example:
    #   <form method="post" id="loginForm" action="..."> ... </form>
    form = soup.find('form', attributes)
    if not form:
        raise ValueError('No form found in HMTL')

    # Check action field to calculate destination of the POST request
    destination = urljoin(url, form['action'])
    # Find all <input> elements with 'name' attributes,
    # then fill a dict with their pre-filled values.
    # Example:
    #   <input id="userNameInput" name="UserName" type="email" value=""/>
    inputs = form.find_all('input', {'name': True})
    data = {i['name']: i.get('value', default_input_value) for i in inputs}

    return Request('POST', destination, data=data)


def verify_ok(r: Response) -> None:
    """Raises `ValueError` if response code is not OK."""
    if r.status_code != codes.ok:
        raise ValueError(f'{r.url} responded with code {r.status_code}.')


def test() -> None:
    """Tests the login process and prints the cookies gathered."""
    print('Testing KTH Canvas login.')
    try:
        s = kth_canvas_login_prompt(verbose=True)
    except ValueError as e:
        print(e)
        return
    print('Got cookies:')
    for c in s.cookies:
        print(c)


if __name__ == '__main__':
    test()

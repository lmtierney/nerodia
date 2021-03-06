import os
import tempfile
from json import load

import pytest


def verify_cookies_count(browser, size):
    cookies = list(browser.cookies)
    assert len(cookies) == size, 'expected {} cookies, ' \
                                 'got {}: {}'.format(size, len(cookies), cookies)


@pytest.fixture
def clear_cookies(browser):
    yield
    browser.cookies.clear()


@pytest.fixture
def verify_cookie(browser):
    verify_cookies_count(browser, 1)


@pytest.fixture
def filepath():
    filepath = os.path.join(tempfile.gettempdir(), 'temp.cookies')
    yield filepath
    if os.path.isfile(filepath):
        os.remove(filepath)


@pytest.mark.page('set_cookie/index.html')
@pytest.mark.usefixtures('clear_cookies', 'verify_cookie')
class TestBrowserCookies(object):
    def test_gets_an_empty_list_of_cookies(self, browser, page):
        browser.goto(page.url('collections.html'))
        browser.cookies.clear()
        assert list(browser.cookies) == []

    def test_gets_any_cookies_set(self, browser):
        cookie = list(browser.cookies)[0]
        assert cookie.get('name') == 'monster'
        assert cookie.get('value') == '1'

    #
    # __getitem__

    def test_returns_cookie_by_name(self, browser):
        cookie = browser.cookies['monster']
        assert cookie.get('name') == 'monster'
        assert cookie.get('value') == '1'

    def test_returns_none_if_there_is_no_cookie_with_such_name(self, browser):
        assert browser.cookies['non_monster'] is None

    def test_adds_a_cookie(self, browser, page, bkwargs):
        # Use temp browser for safari
        temp_browser = browser.__class__(**bkwargs)
        try:
            temp_browser.goto(page.url('set_cookie/index.html'))
            verify_cookies_count(temp_browser, 1)
            temp_browser.cookies.add('foo', 'bar')
            verify_cookies_count(temp_browser, 2)
        finally:
            temp_browser.close()

    def test_removes_a_cookie(self, browser):
        browser.cookies.delete('monster')
        verify_cookies_count(browser, 0)

    # TODO: xfail safari
    def test_clears_all_cookies(self, browser):
        browser.cookies.add('foo', 'bar')
        verify_cookies_count(browser, 2)
        browser.cookies.clear()
        verify_cookies_count(browser, 0)

    def test_saves_cookies_to_file(self, browser, filepath):
        browser.cookies.save(filepath)
        with open(filepath, 'r+') as cookies:
            assert load(cookies) == list(browser.cookies)

    def test_loads_cookies_from_file(self, browser, filepath):
        browser.cookies.save(filepath)
        browser.cookies.clear()
        browser.cookies.load(filepath)

        expected = list(browser.cookies)
        with open(filepath, 'r+') as cookies:
            actual = load(cookies)

        # https://code.google.com/p/selenium/issues/detail?id=6834
        for each in expected:
            each.pop('expires', None)
            each.pop('expiry', None)
        for each in actual:
            each.pop('expires', None)
            each.pop('expiry', None)

        assert actual == expected

"""
(c) 2018 Mario Orlandi, Brainstorm S.n.c.

Helper for Djago unit-testing.

Adapted from: `djest: "Better tests for django" <https://github.com/metzlar/djest>`_
"""

__author__    = "Mario Orlandi"
__version__   = "1.0.1"
__copyright__ = "Copyright (c) 2018, Brainstorm S.n.c."
__license__   = "GPL"


from django.test import TransactionTestCase
#from django.test import TestCase
try:
    from django.urls import reverse_lazy
except:
    from django.core.urlresolvers import reverse_lazy
from django.conf import settings
from django.core import mail
from django.http.response import HttpResponseRedirect
#from .base_testcase import BaseTestCase

from uuid import uuid4
from bs4 import BeautifulSoup
import json
import webbrowser
#from django.contrib.auth.models import User
from django.contrib.auth.models import Group

#
#    From: `djest: "Better tests for django" <https://github.com/metzlar/djest>`_
#
#    Example of testing a custom Admin form:
#
#        from djest.admin import AdminCase
#        from yourapp.models import MyModel
#
#        class MyCase(AdminCase):
#
#            def setUp(self):
#              (
#                self.user_name,
#                self.user_pass,
#                self.user
#              ) = self.create_user(is_staff = True)
#
#              self.new('example', MyModel, { # this is short for:
#                'name': 'Example'            # self['example'] = MyModel(name='Example')
#              })                             # self['example'].save()
#
#            def test_example(self):
#
#              self.assertTrue('example' in self)
#              self.assertTrue(self['example'].name == 'Example')
#
#              #login
#              self.login(self.user_name, self.user_pass)
#
#              # go to the changelist page
#              self.get(reverse('admin:yourapp_mymodel_changelist')
#
#              # count the no. of models on the page
#              self.assert_result_count(1)
#
#              # add another one through the admin
#              self.post(
#                reverse('admin:yourapp_mymodel_add'),
#                {'name': 'Another example instance'}
#              )
#
#              # count again
#              self.assert_result_count(2)
#


class BaseCase(TransactionTestCase, dict):

    def __init__(self, *args, **kwargs):
        super(BaseCase, self).__init__(*args, **kwargs)

    def assert_redirect_to(self, part):
        self.assertTrue(
            isinstance(self.response, HttpResponseRedirect)
        )
        self.assertTrue(
            part in self.response.url
        )

    def assert_mail_count(self, n):
        self.assertEqual(len(mail.outbox), n)

    def reverse(self, *args, **kwargs):
        return reverse_lazy(*args, **kwargs)

    def content(self):
        content = None
        if hasattr(self.response, 'rendered_content'):
            content = self.response.rendered_content
        elif hasattr(self.response, 'content'):
            content = self.response.content
        return content

    def json(self):
        try:
            return json.loads(self.content())
        except:
            return None

    def wout(self):
        '''
        Write out the current response's rendered_content
        to a file in /tmp/out.html TODO: Use temporary
        builtin python module.
        '''
        content = self.content()

        self.debug(content)
        if content:
            with open('/tmp/out.html', 'w') as f:
                try:
                    f.write(content)
                except:
                    f.write(content.encode('utf8'))

            webbrowser.open('file://' + '/tmp/out.html')

    def debug(self, message):
        '''
        Utility method for debugging. Make sure
        settings.TEST_DEBUG is defined and set to
        True. When used, self.debug_buffer will contain
        concatinated debug messages.
        '''
        if (not hasattr(settings, 'TEST_DEBUG')) or (
            not settings.TEST_DEBUG
        ):
            return
        if not hasattr(self, 'debug_buffer'):
            self.debug_buffer = ''
        try:
            message = BeautifulSoup(message).body.get_text()
        except:
            pass

        while '\n\n' in message:
            message = message.replace('\n\n', '\n')

        self.debug_buffer += (
             message +
            '\n------------------------------\n'
        )

    def nop(*args, **kwargs):
        # use for mocking
        # don't do anything
        pass

    def new(self, name, klass, m_kwargs ):
        if name in self:
            raise ValueError('Model already exists %s' % name)
        m = klass(**m_kwargs)
        m.save()
        self[name] = m
        return m

    def post(self, url, data):
        self.response = self.client.post(
            url,
            data,
            follow = True
        )

        if hasattr(
            self.response, 'context'
        ) and self.response.context:

            #if 'errorlist' in self.response.context.keys():
            if 'errorlist' in self.response.context_data.keys():
                self.wout()
                raise Exception('Form did not validate?')

            #if 'form' in self.response.context:
            if 'form' in self.response.context_data:
                if self.response.context['form']._errors:
                    self.wout()
                    raise Exception('Form did not validate?')

            # Added by M.O. Experimental ...
            if 'errors' in self.response.context_data.keys():
                self.wout()
                raise Exception('Form did not validate?')

            # Added by M.O. Experimental ...
            if 'adminform' in self.response.context_data:
                if self.response.context['adminform'].form._errors:
                    self.wout()
                    raise Exception('Form did not validate?')


        return self.response

    def get(self, url):
        self.response = self.client.get(url)
        return self.response

    def uuid4(self):
        return uuid4().hex

    def assert_in_title(self, test):
        soup_title = BeautifulSoup(
            self.response.rendered_content
        ).title.get_text().lower()
        test = test.lower()
        if not test in soup_title:
            raise AssertionError('%s is not in %s' % (
                test,
                soup_title
            ))
        self.assertTrue(True)


class AdminCase(BaseCase):
    def assert_result_count(self, n):
        try:
            self.assertEqual(
                self.response.context['cl'].result_count,
                n
            )
        except KeyError:
            self.wout()
            self.assertEqual(-1, n)

    def assert_not_authorized(self):
        try:
            self.assertEqual(
                self.response.status_code,
                403
            )
        except AssertionError:
            self.wout()
            raise

    def login(self, user_name, user_pass):
        self.response = self.client.login(
            username = user_name,
            password = user_pass
        )
        return self.response

    def logout(self):
        self.response = self.client.logout()
        return self.response

    def reverse(self, name, *args, **kwargs):
        if not ':' in name:
            name = 'admin:%s' % name
        elif name[0] == ':':
            name = name[1:]
        return super(AdminCase, self).reverse(
            name, *args, **kwargs)

    def get_or_create_group(self, name):
        group, created = Group.objects.get_or_create(name=name)
        return group

    # def create_user(self, groups=None, do_login=False, **kwargs):
    #     user_name = self.uuid4()
    #     user_pass = self.uuid4()
    #
    #     user = User.objects.create_user(
    #         user_name,
    #         '%s@djest.generated' % user_name,
    #         user_pass
    #     )
    #
    #     for group in groups or []:
    #         user.groups.add(group)
    #
    #     for k, v in kwargs.iteritems():
    #         setattr(user, k, v)
    #
    #     user.save()
    #
    #     if do_login:
    #         self.login(user_name, user_pass)
    #
    #     self[user_name] = user
    #
    #     return user_name, user_pass, user


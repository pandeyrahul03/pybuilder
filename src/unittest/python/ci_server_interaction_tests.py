#   -*- coding: utf-8 -*-
#
#   This file is part of PyBuilder
#
#   Copyright 2011-2015 PyBuilder Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import unittest
from mock import patch, call

from pybuilder.core import Project
from pybuilder.ci_server_interaction import (test_proxy_for,
                                             TeamCityTestProxy,
                                             TestProxy)


class TestProxyTests(unittest.TestCase):

    def setUp(self):
        self.project = Project('basedir')

    def test_should_use_teamcity_proxy_if_project_property_is_set(self):
        self.project.set_property('teamcity_output', True)

        proxy = test_proxy_for(self.project)

        self.assertEquals(type(proxy), TeamCityTestProxy)

    def test_should_use_default_proxy_if_project_property_is_not_set(self):
        self.project.set_property('teamcity_output', False)

        proxy = test_proxy_for(self.project)

        self.assertEquals(type(proxy), TestProxy)

    def test_should_use_default_proxy_if_project_property_is_set_but_coverage_is_running(self):
        self.project.set_property('teamcity_output', True)
        self.project.set_property('__running_coverage', True)

        proxy = test_proxy_for(self.project)

        self.assertEquals(type(proxy), TestProxy)


class TeamCityProxyTests(unittest.TestCase):

    @patch('pybuilder.ci_server_interaction.flush_text_line')
    def test_should_output_happypath_test_for_teamcity(self, output):
        with TeamCityTestProxy().and_test_name('important-test'):
            pass

        self.assertEqual(output.call_args_list,
                         [
                             call("##teamcity[testStarted name='important-test']"),
                             call("##teamcity[testFinished name='important-test']")
                         ])

    @patch('pybuilder.ci_server_interaction.flush_text_line')
    def test_should_output_failed_test_for_teamcity(self, output):
        with TeamCityTestProxy().and_test_name('important-test') as test:
            test.fails('booom')

        self.assertEqual(output.call_args_list,
                         [
                             call("##teamcity[testStarted name='important-test']"),
                             call("##teamcity[testFailed name='important-test' message='See details' details='booom']"),
                             call("##teamcity[testFinished name='important-test']")
                         ])

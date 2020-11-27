#!/usr/bin/env python
#
# Copyright (c) 2016-2020 InSeven Limited
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import tempfile
import unittest

import yaml

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.dirname(TESTS_DIR)

sys.path.append(SCRIPTS_DIR)

import incontext
import paths
import utils


class TemporarySite(object):
    """
    Context handler which creates a temporary site for testing.
    """
    
    def __init__(self, configuration):
        self.configuration = configuration
        
    @property
    def path(self):
        return self.temporary_directory.name
    
    def __enter__(self):
        self.pwd = os.getcwd()
        self.temporary_directory = tempfile.TemporaryDirectory()
        
        # Create the configuration file.
        with open(os.path.join(self.temporary_directory.name, "site.yaml"), "w") as fh:
            yaml.dump(self.configuration, fh)
        
        # Create the required directories.
        utils.makedirs(os.path.join(self.temporary_directory.name, "content"))
        utils.makedirs(os.path.join(self.temporary_directory.name, "templates"))
            
        os.chdir(self.temporary_directory.name)
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        os.chdir(self.pwd)
        self.temporary_directory.cleanup()


class PluginsTestCase(unittest.TestCase):
    
    def test_expected_plugins(self):
        instance = incontext.InContext(plugins_directory=paths.PLUGINS_DIR)
        self.assertIsInstance(instance.plugins, incontext.Plugins)
        self.assertEqual(set(instance.plugins.plugins(incontext.PLUGIN_TYPE_COMMAND).keys()),
                             {
                                 "add",
                                 "build",
                                 "build-documentation",
                                 "clean",
                                 "publish",
                                 "serve",
                                 "tests",
                                 "watch",
                             })

    def test_create_test_site(self):
        with TemporarySite(configuration={}) as site:
            self.assertIsNotNone(site.path)
            self.assertTrue(os.path.exists(os.path.join(site.path, "site.yaml")))
            self.assertTrue(os.path.isdir(os.path.join(site.path, "content")))
            self.assertTrue(os.path.isdir(os.path.join(site.path, "templates")))

# -*- coding: iso-8859-1 -*-
"""
MoinMoin - MoinMoin.packages tests

@copyright: 2005 MoinMoin:AlexanderSchremmer
@license: GNU GPL, see COPYING for details.
"""

import unittest
from MoinMoin.Page import Page
from MoinMoin._tests import TestConfig
from MoinMoin._tests import TestSkiped as TestSkipped
from MoinMoin.packages import Package, ScriptEngine, MOIN_PACKAGE_FILE, packLine, unpackLine

class DebugPackage(Package, ScriptEngine):
    """ Used for debugging, does not need a real .zip file. """
    def __init__(self, request, filename):
        Package.__init__(self, request)
        ScriptEngine.__init__(self)
        self.filename = filename

    def extract_file(self, filename):
        if filename == MOIN_PACKAGE_FILE:
            return u"""moinmoinpackage|1
print|foo
ReplaceUnderlay|testdatei|TestSeite2
DeletePage|TestSeite2|Test ...
IgnoreExceptions|True
DeletePage|TestSeiteDoesNotExist|Test ...
IgnoreExceptions|False
AddRevision|foofile|FooPage
DeletePage|FooPage|Test ...
setthemename|foo
#foobar
installplugin|foo|local|parser|testy
""".encode("utf-8")
        else:
            return "Hello world, I am the file " + filename.encode("utf-8")

    def filelist(self):
        return [MOIN_PACKAGE_FILE, "foo"]

    def isPackage(self):
        return True
    
class PackagesTests(unittest.TestCase):
    """ Tests various things in the packages package. Note that this package does
        not care to clean up and needs to run in a test wiki because of that. """

    def setUp(self):
        if not getattr(self.request.cfg, 'is_test_wiki', False):
            raise TestSkipped('This test needs to be run using the test wiki.')
   
    def testBasicPackageThings(self):
        myPackage = DebugPackage(self.request, 'test')
        myPackage.installPackage()
        self.assertEqual(myPackage.msg, "foo\n")
        testseite2 = Page(self.request, 'TestSeite2')
        self.assertEqual(testseite2.getPageText(), "Hello world, I am the file testdatei")
        self.assert_(testseite2.isUnderlayPage())
        self.assert_(not Page(self.request, 'FooPage').exists())

class QuotingTests(unittest.TestCase):
    def testQuoting(self):
        for line in ([':foo', 'is\\', 'ja|', u't|�', u'baAz�'], [], ['', '']):
            self.assertEqual(line, unpackLine(packLine(line)))

import os.path
import shutil
import sys
import unittest

import xmlrunner


def run():
    if os.path.isdir('test-reports'):
        shutil.rmtree('test-reports')

    found_tests = unittest.TestLoader().discover('tests')
    return xmlrunner.XMLTestRunner(output='test-reports').run(found_tests)


if __name__ == '__main__':
    r = run()
    if not r.wasSuccessful():
        sys.exit(1)

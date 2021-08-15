import os

from setuptools import setup, find_packages

try:  # pip >= v10.x
    from pip._internal.req import parse_requirements
    from pip._internal.download import PipSession
except ImportError:
    from pip.req import parse_requirements
    from pip.download import PipSession

from common_python_ui_tests import __version__


# Ref: http://alexanderwaldin.github.io/packaging-python-project.html
def read_requirements():
    """parses requirements from requirements.txt"""
    reqs_path = os.path.join(os.getcwd(), 'requirements.txt')
    install_reqs = parse_requirements(reqs_path, session=PipSession())
    reqs = [str(ir.req) for ir in install_reqs]
    return reqs


# Ref: http://alexanderwaldin.github.io/packaging-python-project.html
def read_test_requirements():
    """parses requirements from test_requirements.txt"""
    reqs_path = os.path.join(os.getcwd(), 'test_requirements.txt')
    if os.path.exists(reqs_path):
        install_reqs = parse_requirements(reqs_path, session=PipSession())
        reqs = [str(ir.req) for ir in install_reqs]
        return reqs
    else:
        return []


# override auto-naming
os.environ["pypi_package_name"] = 'common-python-ui-test'

# Add build number if available
buildnumber = os.getenv('buildNumber')
branch = os.getenv('planRepository_branchName')
if buildnumber is not None and branch is not None:
    if branch == 'master':
        os.environ['pypi_package_version'] = '{0}'.format(__version__)
    elif branch == 'develop':
        os.environ['pypi_package_version'] = '{0}.dev{1}'.format(__version__, buildnumber)
    elif 'hotfix/' in branch:
        os.environ['pypi_package_version'] = '{0}.post{1}'.format(__version__, buildnumber)
    elif 'release/' in branch:
        os.environ['pypi_package_version'] = '{0}.rc{1}'.format(__version__, buildnumber)
    else:
        os.environ['pypi_package_version'] = '{0}.feature{1}'.format(__version__, buildnumber)
else:
    os.environ['pypi_package_version'] = '{0}+local.{1}'.format(__version__, os.getenv('USER'))

setup(
    name=os.environ["pypi_package_name"],
    version=os.environ["pypi_package_version"],
    author='Alexander Kekkonen',
    author_email='email_adress',
    maintainer='maintainer_name',
    maintainer_email='maintainer_email',
    description='My awesome lib',
    project_urls={
          "Source Code": 'https://github.com/alkekkonen/common-python-ui-tests.git',
    },
    packages=find_packages(exclude=['tests*']),
    install_requires=read_requirements(),
    include_package_data=False
)

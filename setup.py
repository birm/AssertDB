from distutils.core import setup

setup(name='AssertDB',
      version='0.0.1',
      description='A Database Precondition and Assertion Tool',
      author='Ryan Birmingham',
      author_email='birm@rbirm.us',
      url='http://rbirm.us',
      classifiers=['Development Status :: 1 - Planning',
                   'Topic :: Database',
                   'Intended Audience :: Information Technology',
                   'Programming Language :: SQL',
                   'Programming Language :: Python :: 2.7'],
      long_description=open('README.md', 'r').read(),
      packages=['AssertDB'],
      )

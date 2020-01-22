import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()


requires = [
    'pyramid==1.7',
    'pyramid-jinja2==2.6.2',
    'pyramid-debugtoolbar==3.0.2',
    'pyramid_debugtoolbar',
    'pyramid-tm==0.12.1',
    'authomatic==0.1.0.post1',
    'cornice==1.2.1',
    'sqlalchemy==1.1.0b2',
    'transaction==1.6.1',
    'zope.sqlalchemy==0.7.7',
    'facebook_sdk>=3.0.0-alpha',
    'waitress==1.0a2',
    'psycopg2==2.7',
    'python-dateutil==2.5.3',
    'nose'
    ]

setup(name='social_insights',
      version='0.0',
      description='social_insights',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='social_insights',
      install_requires=requires,
      dependency_links = ['https://github.com/mobolic/facebook-sdk/archive/d1e9a4f458fb5ee35e6ecdc034e2a51cf9c0f7b0.zip#egg=facebook_sdk-3.0.0-alpha'],
      entry_points="""\
      [paste.app_factory]
      main = social_insights:main
      [console_scripts]
      initialize_social_insights_db = social_insights.scripts.initializedb:main
      collect_fb_posts = social_insights.datacollection.fb_posts_collector:main
      learn_models = social_insights.scripts.learn_model:main
      apply_models = social_insights.scripts.apply_model:main
      """
      )

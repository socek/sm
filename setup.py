# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'pyramid',
    'pyramid_jinja2',
    # 'uwsgi',
    'pytest-cov',
    'pytest',
    'ipdb',
    'waitress',
    'sqlalchemy',
    'zope.sqlalchemy',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'mock',
]
dependency_links = [

]

if __name__ == '__main__':
    setup(name='sm',
          version='0.1.1',
          packages=find_packages('src'),
          package_dir={'': 'src'},
          install_requires=install_requires,
          dependency_links=dependency_links,
          include_package_data=True,
          entry_points="""\
            [paste.app_factory]
                main = sm.application:main
            [console_scripts]
                initialize_sm_db = sm.scripts.initializedb:main
          """,
          )

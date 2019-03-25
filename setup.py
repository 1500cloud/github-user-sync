#!/usr/bin/env python3

from setuptools import setup

setup(name='github_user_sync',
      version='1.0.dev',
      description='synchronises users between G Suite and a GitHub org',
      url='https://github.com/1500cloud/github-user-sync/',
      author='Chris Northwood',
      author_email='chris.northwood@1500cloud.com',
      license='GNU General Purpose License v3',
      packages=['github_user_sync'],
      install_requires=[
            'google-api-python-client ~= 1.7',
            'google-auth ~= 1.6',
            'PyGithub ~= 1.43',
      ],
      scripts=['bin/sync-github-users'])

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = ['decorator',
            'pycrypto',
]

test_requires = [
  'mock',
  'nose',
]

setup(name='HolviClient',
      version = "1.0",
      description='Holvi.org Python Client Library',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Distributed Computing",
        "Topic :: Utilities",
        ],
      author='Holvi.org Secure Cloud Infrastructure (SCI)',
      author_email='support.dev@holvi.org',
      url='http://www.holvi.org/',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=requires,
      tests_require=requires,
      test_suite="holvi",
      entry_points="""\
      [console_scripts]
      holvi-cli = holvi.cli:main
      """
      )

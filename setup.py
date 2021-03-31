import os
import sys

from setuptools import setup
from setuptools.command.install import install

# Package Version
VERSION = "0.2.6"


def readme():
    """print long description"""
    with open('README.md') as f:
        return f.read()


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


setup(
    name='vectrix',
    packages=['vectrix', 'vectrix.graphql'],
    version=VERSION,
    license='MIT',
    description='Vectrix Developer Python Package',
    long_description=readme(),
    author='Matthew Lewis',
    author_email='matthew.lewis@vectrix.io',
    url='https://github.com/VectrixSecurity/Vectrix-Python',
    keywords=['vectrix', 'vectrixio', 'vectrix.io', 'vectrix module'],
    install_requires=[
        'requests==2.22.0',
        'boto3==1.15.17',
        'sentry-sdk==1.0.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)

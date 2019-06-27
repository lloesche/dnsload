import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="dnsload",
    version="0.0.1",
    description="Simple DNS load tool",
    license="Apache 2.0",
    long_description=read('README.md'),
    packages=['dnsload'],
    entry_points={
        'console_scripts': [
            'dnsload = dnsload:main'
        ],
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'dnslib'
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    classifiers=[
        # Current project status
        'Development Status :: 4 - Beta',

        # Audience
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',

        # License information
        'License :: OSI Approved :: Apache Software License',

        # Supported python versions
        'Programming Language :: Python :: 3.7',

        # Supported OS's
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',

        # Extra metadata
        'Environment :: Console',
        'Natural Language :: English',
        'Topic :: Security',
        'Topic :: Utilities',
    ],
    keywords='dns load-testing'
)

import codecs
from setuptools import setup, find_packages

setup(
    name='fifofile',
    version='1.0.0',
    description='FiFoFile is a class that makes it easy to read and write lines in fifo files (named pipes)',
    url='https://github.com/rabuchaim/fifofile',
    author='Ricardo Abuchaim',
    author_email='ricardoabuchaim@gmail.com',
    maintainer='Ricardo Abuchaim',
    maintainer_email='ricardoabuchaim@gmail.com',
    project_urls={
        "Issue Tracker": "https://github.com/rabuchaim/fifofile/issues",
        "Source code": "https://github.com/rabuchaim/fifofile",
    },    
    bugtrack_url='https://github.com/rabuchaim/fifofile/issues',    
    license='MIT',
    keywords=['fifo','fifofile','fifo file','named','named pipes','named pipe','epoll','select','poll','polling','syslog-ng','syslog','rsyslog'],
    packages=['fifofile'],
    py_modules=['fifofile', 'fifofile'],
    package_dir = {'fifofile': 'fifofile'},
    include_package_data=True,
    zip_safe = False,
    package_data={
        'fifofile': [
            'README.md',
            'LICENSE',
            'fifofile/fifofile.py',
            'fifofile/__init__.py',
        ],
    },
    python_requires=">=3.0",
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Security',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: Microsoft :: Windows :: Windows 11',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',  
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
    ],
    long_description=codecs.open("README.md","r","utf-8").read(),
    long_description_content_type='text/markdown',
)

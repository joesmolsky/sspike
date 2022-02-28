from setuptools import setup, find_packages

with open('README.md', mode='r') as readme:
    long_description = readme.read()

setup(
    name='sspike',
    version='0.0.1',
    author='Joe Smolsky',
    author_email='smolsky@mit.edu',
    description='snewpy supernovae package inducing KamLAND events',
    license='MIT License',
    keywords='KamLAND kamland supernovae',
    url='https://github.com/joesmolsky/sspike',
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=['Development Status :: 5 - Alpha',
                 'Programming Language :: Python :: 3.8',
                 'Operating System :: MacOS',
                 'License :: OSI Approved :: MIT License', ],
    install_requires=['numpy', 'matplotlib', ],
    extras_require={'dev':
                    ['pytest', 'sphinx', 'pydata_sphinx_theme',
                     # 'ipython', 'pylint', 'hypothesis'
                     ], },
    # entry_points = {
    #     'console_scripts': ['sspike=sspike.sspike:main']
    # }
)

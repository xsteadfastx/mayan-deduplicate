from setuptools import setup


setup(
    name='mayan-deduplicate',
    version='0.0.2',
    py_modules=['mayan_deduplicate'],
    install_requires=[
        'click>=6.7.0',
        'requests>=2.13.0',
        'pendulum>=1.0.2',
    ],
    entry_points='''
        [console_scripts]
        mayan-deduplicate=mayan_deduplicate:ui
    '''
)

from setuptools import setup

setup(
    name='shopify2woo',
    version='0.1',
    py_modules=['s  hopify2woo'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        shopify2woo=shopify2woo:cli
    ''',
)

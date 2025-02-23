from setuptools import setup, find_packages

setup(
    name='pyvotab',
    version='0.0.1',
    description='special prepared Excel tables for simple compare between versions',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'openpyxl'
    ],
    author='Steffen Köhler',
    author_email='steffen@koehlers.de',
    keywords=['excel','diff'],
    url='https://github.com/stko/pyvotab'
)
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='ecs_engine',
    version='0.5.0',
    packages=find_packages(),
    install_requires=[],
    
    #
    author='Jacob Simerly',
    author_email='simerly81@gmail.com',
    description='This is an ECS Engine for building game in python.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='ECS Entity Component System pygame',
    url='https://github.com/jsimerly/ecs_engine'
)
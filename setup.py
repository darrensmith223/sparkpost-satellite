from setuptools import setup, find_packages


setup(
    name='sparkpostsatellite',
    version='1.0.0',
    author='Darren Smith',
    author_email='darren.smith@sparkpost.com',
    packages=find_packages(),
    url='https://github.com/darrensmith223/sparkpost-satellite',
    license='Apache 2.0',
    description='Linking SparkPost Accounts Together',
    install_requires=['requests>=2.20.1']
)
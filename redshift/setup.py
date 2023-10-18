from setuptools import setup

setup(name='redshift_management',
version='0.1',
description='Testing installation',
url='#',
author='Charis Petsas',
author_email='c.petsas@rheagroup.com',
license='MIT',
packages=['redshift_management'],
install_requires=   ['boto3==1.16.56',
                    'botocore==1.19.56',
                    'jmespath==0.10.0',
                    'psycopg2-binary==2.8.6',
                    'python-dateutil==2.8.1',
                    's3transfer==0.3.4',
                    'six==1.15.0',
                    'urllib3==1.26.18'],
python_requires='>=3',)
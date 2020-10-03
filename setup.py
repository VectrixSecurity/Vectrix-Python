from distutils.core import setup
setup(
    name='vectrix',
    packages=['vectrix'],
    version='0.1.7',
    license='MIT',
    description='Vectrix Developer Python Package',
    author='Matthew Lewis',
    author_email='matthew.lewis@vectrix.io',
    url='https://github.com/VectrixSecurity/Vectrix-Python',
    download_url='https://github.com/VectrixSecurity/Vectrix-Python/archive/v0.1.7.tar.gz',
    keywords=['vectrix', 'vectrixio', 'vectrix.io', 'vectrix module'],
    install_requires=[
        'requests==2.22.0',
        'boto3==1.14.38',
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
)

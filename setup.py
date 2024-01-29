from setuptools import setup, find_packages

setup(
    name='YourPackageName',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'joblib',
        'google-cloud-storage',
        'nltk',
        'pandas',
        'scikit-learn',
        'python-dotenv',
        'jinja2',
        'mediacloud-api-legacy',
    ],
    entry_points={
        'console_scripts': [
            'your_script_name = your_package.module:main_function',
        ],
    },
    author='Catalina Rojas Ugarte',
    author_email='catalina@welevelup.com',
    description='FEMWatch',
    url='https://github.com/crojasu/femicideMWatch',
    keywords='your, package, keywords',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        # Add more classifiers as needed
    ],
)
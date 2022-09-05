from setuptools import setup, find_packages

setup(
    name="Assume.py",
    author="gatewaynode",
    version="0.1",
    install_requires=[
        "boto3",
        "botocore",
        "cffi",
        "click",
        "cryptography",
        "Jinja2",
        "jmespath",
        "MarkupSafe",
        "mypy-extensions",
        "pathspec",
        "pdoc",
        "platformdirs",
        "pycparser",
        "Pygments",
        "python-dateutil",
        "PyYAML",
        "s3transfer",
        "six",
        "tomli",
        "urllib3",
    ],
    entry_points={
        'console_scripts': [
            'assume' = 'assume_py.main:main'
        ]
    }
)

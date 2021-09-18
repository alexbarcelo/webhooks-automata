import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webhooks-automata",
    version="0.1.0",
    author="Alex Barcelo",
    author_email="alex@betarho.net",
    description="Webhook receiver for deployment automations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["Flask", "PyYAML"],
    url="https://github.com/alexbarcelo/webhooks-automata",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'wh-automatad = webhooks_automata.webhooks:main_func',
            'wh-automata-trigger = webhooks_automata.webhooks:manual_trigger',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

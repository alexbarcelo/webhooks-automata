import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webhooks_git_automata",
    version="0.0.2",
    author="Alex Barcelo",
    author_email="alex@betarho.net",
    description="Webhook receiver for Git deployments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["Flask", "PyYAML"],
    url="https://github.com/alexbarcelo/webhooks-git-automata",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'wh-gitd = webhooks_git_automata.webhooks:main_func',
            'wh-git-trigger = webhooks_git_automata.webhooks:manual_trigger',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

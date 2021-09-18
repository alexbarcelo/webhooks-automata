
Webhook receiver for automations
================================

This project started as a dirty & quick hack to perform some deployment actions.
Initially, the focus was on Git webhooks, but after a while this project was
renamed and the scope was broadened a bit.

I looked a little bit at other projects and didn't found any one that suited my
needs, so I started this project... and then it grew a little bit and become
something more versatile than the quick hack originally intended.

This project is aimed at DevOps or sysadmin that have git repositories, typically
with a VIP-branch, and automatic deployment. You may want to have different branches
for stage and production or set up push permissions differently to the different 
branches. This utility, when a webhook is received, will update the local Git repository
and perform the commands in the settings.

Quickstart
----------

- Create and activate a Virtual Environment:

```bash
$ virtualenv --python=/usr/bin/python3 /path/to/venv
$ source /path/to/venv/bin/activate
```

- Install the package: `pip install webhooks_automata`
- Create a `settings.yaml`
- Set up a service (e.g. a systemd _service_ file) that does something along:

```bash
$ /path/to/venv/bin/wh-automatad /path/to/settings.yaml
```

Settings
--------

Extra CLI features
------------------

To force a manul trigger, you can use
the built-in `wh-automata-trigger` command. Example usage:

```bash
$ wh-git-trigger /path/to/setings.yaml entryname
```

This will react just as if a trigger had been received. Future versions of this tool will
include more fine-grain control --e.g. dry-run, display status information...

Implementation details
----------------------

This project contains a minimal Flask server that answers the POST webhooks. A typical source
of those webhooks call are Git servers such as GitLab, GitHub or Gogs. The server is started
through the Flask's `app.run` method.

Not a lot of traffic is expected, but you may want to set up a reverse proxy in front
of the Flask server, or add some fancier method like a WSGI or uWSGI or similar layer.

Typical webhooks expect the a quick reply (in general, HTTP connections are intended to be short
lived) so there is a worker/tasks approach. There is a very simple implementation base on
`Threading` and a shared `Queue`. More complex implementations may be added in the future
(pull requests are welcome).

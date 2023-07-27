Webhook server for triggering automations
=========================================

This project started as a dirty & quick hack to perform some deployment actions.
Initially, the focus was on Git webhooks, but after a while this project was
renamed and the scope was broadened a bit.

I looked a little bit at other projects and didn't found any one that suited my
needs, so I started this project... and then it grew a little bit and become
something more versatile than the quick hack originally intended.

This project is aimed at DevOps or sysadmin that have git repositories in GitHub, Gitlab,
or any other kind of webhook provider (git or otherwise).

This utility starts a server that listens to webhooks and when a webhook is received,
it will perform the actions in the settings.

Quickstart demo with GitHub and ngrok
-------------------------------------

Using [ngrok](https://ngrok.com/) is a quick way to obtain a publicly reachable HTTPS endpoint.
We will be using that for this demo.

- Create and activate a Virtual Environment in a Python 3.11 environment.
- Install the package: `pip install webhooks-automata`
  - If you want to use `main` branch, do
  `pip install git+https://github.com/alexbarcelo/webhooks-automata`
  instead.
- Create a `settings.yaml`, like the one shown in [examples](examples/github_sample.yaml).
- Start the server:

```bash
$ AUTOMATA_SETTINGS=examples/github_sample.yaml uvicorn webhooks_automata.app:app
INFO:     Started server process [57971]
INFO:     Waiting for application startup.
Current endpoints active:
        /my_webhook
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

- Run the ngrok ingress to this service with `ngrok http 8000`
- The webhook endpoint will be something like `https://c94e-2600-70ff-f2f3-0-13ef-f451-8b4f-cc76.ngrok-free.app/my_webhook`
(the host on this URL is given by ngrok and the path is set in the settings YAML file).
- Go to your GitHub repository > Settings > Webhooks > Add webhook.
- Fill the form:
  - **Payload URL**: The webhook endpoint.
  - **Content type**: Does not matter, but use JSON for future proofing it.
  - **Secret**: Put the shared secret in the settings YAML file, in this demo it is `secret_token`
  - _Add webhook_
- When a webhook is created, GitHub makes a "ping delivery". You can check in the Recent Deliveries
tab if there was a problem with the webhook endpoint.

If you are using ngrok, remember that you can diagnose stuff by going to http://127.0.0.1:4040

Deploying the webhook server
----------------------------

Instead of using ngrok, you may want to deploy this application into a
domain/server under your control. The steps are similar like on the previous
demo, but you will need to include a reverse proxy (and you probably want
to include SSL termination on it).

Take a look into [nginx](https://nginx.org/), [Traefik](https://traefik.io/)
or [HAProxy](https://www.haproxy.org/).

In addition to that, you will want to automatically start the Uvicorn server,
which may done with either systemd (or whatever is used by your OS) or
[supervisord](http://supervisord.org/).

Settings
--------

Extra CLI features
------------------

The `wh-automatactl` is a CLI that can be used to aid and complement the webhook server.

You can check its documentation by calling `wh-automatactl --help`. Keep in mind that this
CLI will be accessible from within the virtual environment; that typically means that the
script can be found in /pat/to/venv/bin/wh-automatactl.

Implementation details
----------------------

This project contains a minimal [Starlette](https://www.starlette.io/) ASGI
application that answers the POST webhooks. My recommendation is to start the
application through [uvicorn](http://www.uvicorn.org/).

The actions are run as [Starlette Background Tasks](https://www.starlette.io/background/)
because generally providers (GitHub, Gitlab, etc.) expect a quick webhook and
do not care on the return. A 200 success response is given for all properly
authorized requests and actions are run after that; a 200 success response
**does not mean** that actions have run successfully (in fact, the actions start
**after** the response).

Most internal code assumes that things can be made asynchronously, so the
webhook server should be a lightweight but capable process --the heavy-lifting
will be performed by asynchronous actions. This is assured by using 
[`asyncio-subprocess`](https://docs.python.org/3/library/asyncio-subprocess.html)
and other async-centric tools.

Feel free to use other ASGI servers, or embed the Starlette routes into a more
complex application.

from logging import getLogger
import hmac

from flask import request
from werkzeug.exceptions import Forbidden, BadRequest

from .worker import event_queue

logger = getLogger(__name__)


def _schedule_data_from_request():
    """Given an ongoing request, schedule it to the worker.

    This can be called from an ongoing request, and it will get the data (the
    JSON payload) and put it in the worker event_queue for later processing.
    """
    data = request.get_json(force=True, cache=False)
    if not data:
        raise BadRequest("Unconsistent JSON received")
    event_queue.put(data)


def webhook_github(secret):
    """GitHub implementation of the webhook (requires secret)."""
    logger.debug("Received a POST from: %s",
                 request.remote_addr)

    agent = request.headers.get("User-Agent")

    if not agent.startswith("GitHub-Hookshot"):
        raise Forbidden("Only GitHub is allowed to POST to us")

    signature = request.headers.get("X-Hub-Signature")
    event_type = request.headers.get("X-GitHub-Event")

    if not signature or not event_type:
        raise Forbidden("Webhooks must include the signature "
                        "(add `secret` to the webhook settings in GitHub)")

    if not secret:
        raise SystemError("No `secret` configured, refusing to accept petition")

    try:
        digest = hmac.digest(secret, request.get_data(), "sha1")
    except AttributeError:  # Python < 3.7, using older & slower approach
        h = hmac.new(secret, request.get_data(), "sha1")
        digest = h.digest()

    # Strip the first five characters: 'sha1=xxxxxxx' and get it in binary form
    sent_digest = bytes.fromhex(signature[5:])
    if digest != sent_digest:
        logger.debug("Expected signature %s, received %s" % (digest, sent_digest))
        raise Forbidden("The HMAC digest do not match. You are not allowed.")

    if event_type == "ping":
        logger.info("Ignoring ping event")
    else:
        _schedule_data_from_request()

    return ""


def webhook_gogs(secret):
    """Gogs implementation of the webhook (requires secret)."""
    logger.debug("Received a POST from: %s",
                 request.remote_addr)

    data = request.get_json(force=True, cache=False)
    if not data:
        raise BadRequest("Unconsistent JSON received")

    try:
        if data["secret"] != secret:
            logger.debug("Received secret: %s, which did not match the expected", data["secret"])
            raise Forbidden("Invalid `secret` provided in HTTP method payload")
    except KeyError:
        raise Forbidden("The request should include the `secret`. "
                        "Have you configured correctly the gogs sever webhook?")

    event_queue.put(data)
    return ""


def webhook_plain():
    """Trivial implementation."""
    logger.debug("Received a POST from: %s",
                 request.remote_addr)

    _schedule_data_from_request()

    return ""

from logging import getLogger
from werkzeug.exceptions import Forbidden
import hmac

from .base_classes import GitAutomaton

logger = getLogger(__name__)


class GitHubAutomaton(GitAutomaton):
    """Automaton for GitHub webhooks.
    
    This automaton requires a `secret` config entry.
    """
    def receive_webhook(self, request):
        agent = request.headers.get("User-Agent")

        if not agent.startswith("GitHub-Hookshot"):
            raise Forbidden("Only GitHub is allowed to POST to us")

        signature = request.headers.get("X-Hub-Signature")
        event_type = request.headers.get("X-GitHub-Event")

        if not signature or not event_type:
            raise Forbidden("Webhooks must include the signature "
                            "(add `secret` to the webhook settings in GitHub)")

        secret = self._provider_opts.get("secret")
        if not secret:
            raise SystemError("No `secret` configured, refusing to accept petition")

        try:
            # We need a bytes object, if secret is a str then we should encode it
            secret = secret.encode("ascii")
        except AttributeError:
            # Hopefully it failed because it already is a bytes object
            pass

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
            data = request.get_json(force=True, cache=False)
            self._schedule(data)

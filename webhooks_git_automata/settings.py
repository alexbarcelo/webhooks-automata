import logging

import yaml

from .automata import Automata

logger = logging.getLogger(__name__)


class Configuration(object):
    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            cls._settings = yaml.load(f)

        # Logging settings
        logging.basicConfig(level=cls._settings.get("log_level", "INFO"))
        logger.info("Initialized with configuration at %s", path)
        logger.debug("Debug level is activated")

        # Provider settings
        provider = cls._settings.get("provider", "plain")

        if isinstance(provider, dict):
            # If it is a dictionary, the provider is the key name
            cls.provider = provider.pop("name")
            # and all other entries are their options
            cls.provider_options = provider
        else:
            # typically "plain", which has no extra configuration
            cls.provider = provider
            cls.provider_options = dict()

        # URL path for webhooks
        cls.webhook_url_path = cls._settings.get("webhook_url_path", "/webhook")

        # IP to listen to
        cls.listen_ip = cls._settings.get("listen_ip", "127.0.0.1")

        # Port to listen to
        cls.listen_port = cls._settings.get("listen_port", 5000)

        # Repositories required entry, (managed by the `Actions` class)
        Automata.load_config(cls._settings["repositories"])

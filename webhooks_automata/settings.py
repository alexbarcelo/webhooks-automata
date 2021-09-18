import logging

import yaml

from .automata import automata, automaton_classes

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

        # Base URL path for webhooks
        cls.webhook_url_path = cls._settings.get("webhook_url_path", "/webhook")

        # IP to listen to
        cls.listen_ip = cls._settings.get("listen_ip", "127.0.0.1")

        # Port to listen to
        cls.listen_port = cls._settings.get("listen_port", 5000)

        # Global configuration for each provider
        provider_configs = {"plain": {}}
        for name, config in cls._settings.get("providers", {}).items():
            provider_configs[name] = config

        # "automata" must exist, otherwise the application has nothing to do
        for name, automaton in cls._settings["automata"].items():
            # Which provider to use:
            provider = cls._settings.get("provider", "plain")

            provider_options = provider_configs[provider]
            provider_options.update(automaton.get("provider_options", {}))

            config = automaton.get("config", {})
            action = automaton.get("action", {})

            automaton_class = automaton_classes[provider]
            automaton_instance = automaton_class(name, provider_options, config, action)

            automata.add_automaton(name, automaton_instance)

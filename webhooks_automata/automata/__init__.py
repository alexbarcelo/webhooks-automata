from .gogs import GogsAutomaton
from .github import GitHubAutomaton
from .plain import PlainAutomaton


automaton_classes = {
    "plain": PlainAutomaton,
    "github": GitHubAutomaton,
    "gogs": GogsAutomaton,
}

# Singleton instance containing all automaton
automata = dict()

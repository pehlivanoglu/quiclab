class QuiclabError(Exception):
    pass


class ConfigError(QuiclabError):
    pass


class OrchestratorError(QuiclabError):
    pass


class RunNotFoundError(QuiclabError):
    pass


class RunAlreadyExistsError(QuiclabError):
    pass

def get_metacritic_provider():
    from flask import g

    if 'metacritic_provider' not in g:
        from .metacritic import MetacriticProvider
        g.metacritic_provider = MetacriticProvider()

    return g.metacritic_provider

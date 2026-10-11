"""Model registry: name -> factory of a fresh unfitted model with fit(X, y) / predict_proba(X)."""
from alerts.models.baselines import BASELINES
from alerts.models.learned import LEARNED


def registry(cfg: dict, names: list, params: dict | None = None) -> dict:
    """Factories for the named models. Learned models need their tuned `params[name]`."""
    out = {}
    for name in names:
        if name in BASELINES:
            out[name] = (lambda cls=BASELINES[name]: cls(cfg))
        elif name in LEARNED:
            if not params or name not in params:
                raise KeyError(f'{name} needs tuned parameters')
            out[name] = (lambda cls=LEARNED[name], p=params[name]: cls(cfg, p))
        else:
            raise KeyError(f'unknown model {name}')
    return out

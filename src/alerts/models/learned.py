"""Learned models of PLAN stage 6 (D20): M1 logistic regression, M2 LightGBM.

Same interface as the baselines: fit(X, y) / predict_proba(X), where X is the backtest frame.
Every fit starts from scratch: scaling, imputation and category lists are learned on the
training rows of that backtest step only (PLAN rule 3). Optional recency weighting gives a row of
age a days the weight 0.5 ** (a / half_life_days); the age is counted from the last training row.
"""
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from alerts.features import NUMERIC

LR_FEATURES = [f for f in NUMERIC if f not in ('hour_kyiv', 'dow_kyiv')]        # cyclic sin/cos instead
GBM_FEATURES = [f for f in NUMERIC if f not in ('hour_sin', 'hour_cos', 'dow_sin', 'dow_cos')] + ['unit_id']


def recency_weights(t: pd.Series, half_life_days) -> np.ndarray | None:
    if half_life_days is None:
        return None
    age = (t.max() - t).dt.total_seconds().to_numpy() / 86400
    return 0.5 ** (age / half_life_days)


class LogisticModel:
    """M1: standardised numeric features (median imputation with missing-value indicators), cyclic
    calendar, one-hot unit identity, L2-regularised logistic regression."""
    name = 'LR'

    def __init__(self, cfg: dict, params: dict):
        self.params = params
        self.cfg = cfg

    def fit(self, X: pd.DataFrame, y: np.ndarray):
        prep = ColumnTransformer([
            ('num', make_pipeline(SimpleImputer(strategy='median', add_indicator=True), StandardScaler()), LR_FEATURES),
            ('unit', OneHotEncoder(handle_unknown='ignore'), ['unit_id'])])
        self.model_ = make_pipeline(prep, LogisticRegression(C=self.params['C'], max_iter=1000))
        w = recency_weights(X['t'], self.params['half_life_days'])
        self.model_.fit(X, y.astype(int), logisticregression__sample_weight=w)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model_.predict_proba(X)[:, 1]


class GBMModel:
    """M2: one LightGBM model for all units; unit identity as a categorical feature."""
    name = 'LGBM'

    def __init__(self, cfg: dict, params: dict):
        self.params = params
        self.cfg = cfg

    def _frame(self, X: pd.DataFrame) -> pd.DataFrame:
        f = X[GBM_FEATURES].copy()
        f['unit_id'] = pd.Categorical(f['unit_id'].astype(str), categories=self.categories_)
        return f

    def estimator(self, n_estimators: int) -> lgb.LGBMClassifier:
        m = self.cfg['models']
        return lgb.LGBMClassifier(
            n_estimators=n_estimators, learning_rate=m['lgbm']['learning_rate'],
            num_leaves=self.params['num_leaves'], min_child_samples=self.params['min_child_samples'],
            subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
            deterministic=True, force_row_wise=True, n_jobs=m['threads'], random_state=m['seed'], verbose=-1)

    def fit(self, X: pd.DataFrame, y: np.ndarray, eval_set=None):
        self.categories_ = sorted(X['unit_id'].astype(str).unique())
        self.model_ = self.estimator(self.params['n_estimators'])
        w = recency_weights(X['t'], self.params['half_life_days'])
        kw = {}
        if eval_set is not None:                       # tuning only: early stopping on validation rows
            Xv, yv = eval_set
            kw = dict(eval_X=self._frame(Xv), eval_y=yv.astype(int), eval_metric='binary_logloss',
                      callbacks=[lgb.early_stopping(self.cfg['models']['lgbm']['early_stopping_rounds'], verbose=False)])
        self.model_.fit(self._frame(X), y.astype(int), sample_weight=w, **kw)
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model_.predict_proba(self._frame(X))[:, 1]

    def gain_importance(self) -> pd.Series:
        b = self.model_.booster_
        g = pd.Series(b.feature_importance(importance_type='gain'), index=b.feature_name())
        return (g / g.sum()).sort_values(ascending=False)


LEARNED = {m.name: m for m in [LogisticModel, GBMModel]}

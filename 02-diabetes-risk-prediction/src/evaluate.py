"""
Reusable functions to measure and plot how well a trained model performs.

Every function takes `models`, a dictionary like {"Logistic Regression": pipeline, ...},
so the same code works for one model or many.
"""

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (ConfusionMatrixDisplay, PrecisionRecallDisplay, RocCurveDisplay,
                             accuracy_score, f1_score, precision_score, recall_score, roc_auc_score)

# Shared chart colours (same as the EDA notebook)
BLUE = "#2a78d6"
ORANGE = "#d9822b"
GREY = "#898781"
MODEL_COLOURS = [ORANGE, BLUE]   # first model orange, second model blue


def predict_with_threshold(model, X, threshold=0.5):
    """
    Turn the model's probabilities into 0/1 predictions.

    model.predict() always uses 0.5. Using the probability ourselves lets us choose a different
    threshold: anyone with a probability >= threshold is predicted as diabetic (1).
    """
    probabilities = model.predict_proba(X)[:, 1]   # column 1 = probability of diabetes
    return (probabilities >= threshold).astype(int)


def get_metrics(model, X, y, threshold=0.5):
    """Return the main scores for one model as a dictionary."""
    predictions = predict_with_threshold(model, X, threshold)
    probabilities = model.predict_proba(X)[:, 1]
    return {
        "precision": precision_score(y, predictions),
        "recall": recall_score(y, predictions),
        "f1": f1_score(y, predictions),
        "roc_auc": roc_auc_score(y, probabilities),   # uses probabilities, so it doesn't depend on the threshold
        "accuracy": accuracy_score(y, predictions),
    }


def metrics_table(models, X, y, threshold=0.5):
    """One row of scores per model."""
    rows = {name: get_metrics(model, X, y, threshold) for name, model in models.items()}
    return pd.DataFrame(rows).T


def plot_confusion_matrices(models, X, y, labels=("No diabetes", "Diabetes")):
    """One confusion matrix per model, side by side."""
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 5))
    for ax, (name, model) in zip(axes, models.items()):
        ConfusionMatrixDisplay.from_predictions(
            y, model.predict(X), display_labels=labels, cmap="Blues",
            values_format=",", colorbar=False, ax=ax)
        ax.set_title(name, fontweight="bold")
        ax.grid(False)
    fig.tight_layout()
    return fig


def plot_roc_curves(models, X, y, ax):
    """ROC curves of all models on one chart, plus the random-guess line."""
    for (name, model), colour in zip(models.items(), MODEL_COLOURS):
        RocCurveDisplay.from_estimator(model, X, y, name=name, ax=ax,
                                       curve_kwargs={"color": colour, "linewidth": 2})
    ax.plot([0, 1], [0, 1], linestyle="--", color=GREY, label="Random guess (AUC = 0.5)")
    ax.set_title("ROC curve", loc="left", fontweight="bold")
    ax.set_xlabel("False positive rate (healthy people wrongly flagged)")
    ax.set_ylabel("True positive rate (recall)")
    ax.legend(loc="lower right")


def plot_precision_recall_curves(models, X, y, ax):
    """Precision-recall curves of all models on one chart, plus the random-guess line."""
    for (name, model), colour in zip(models.items(), MODEL_COLOURS):
        PrecisionRecallDisplay.from_estimator(model, X, y, name=name, ax=ax,
                                       curve_kwargs={"color": colour, "linewidth": 2})
    # A random guess has precision equal to the share of diabetes cases, at every recall
    ax.axhline(y.mean(), linestyle="--", color=GREY, label=f"Random guess (AP = {y.mean():.2f})")
    ax.set_title("Precision-recall curve", loc="left", fontweight="bold")
    ax.set_xlabel("Recall (share of diabetes cases found)")
    ax.set_ylabel("Precision (share of flags that are correct)")
    ax.legend(loc="upper right")


def threshold_table(model, X, y, thresholds=(0.3, 0.4, 0.5, 0.6)):
    """How precision, recall and the number of missed cases change with the threshold."""
    rows = []
    for threshold in thresholds:
        predictions = predict_with_threshold(model, X, threshold)
        rows.append({
            "threshold": threshold,
            "precision": precision_score(y, predictions),
            "recall": recall_score(y, predictions),
            "f1": f1_score(y, predictions),
            "people_flagged": int(predictions.sum()),
            "diabetes_cases_missed": int(((predictions == 0) & (y == 1)).sum()),
        })
    return pd.DataFrame(rows)


def plot_top_features(values, title, xlabel, ax, top_n=10):
    """
    Horizontal bar chart of the top_n features by size (absolute value).
    Positive values are blue, negative values orange.
    """
    top = values.reindex(values.abs().sort_values(ascending=False).index).head(top_n)
    top = top[::-1]   # reverse so the biggest bar is at the top
    colours = [BLUE if v > 0 else ORANGE for v in top]
    ax.barh(top.index, top.values, color=colours)
    ax.axvline(0, color=GREY, linewidth=1)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_xlabel(xlabel)

"""
Prepare the data for modelling: split it into train/test sets and build model pipelines.
"""

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

TARGET = "Diabetes_binary"   # the column we want to predict


def split_data(df, target=TARGET, test_size=0.2, random_state=42):
    """
    Split the data into a training set (80%) and a test set (20%).

    - X = the features (inputs), y = the target (the answer we want to predict).
    - stratify=y keeps the same share of diabetes cases in both sets (about 15% each),
      so the test set is a fair, representative sample.
    - random_state=42 makes the split identical every time we run it, so results are reproducible.

    Returns: X_train, X_test, y_train, y_test
    """
    X = df.drop(columns=target)
    y = df[target]
    return train_test_split(X, y, test_size=test_size, stratify=y, random_state=random_state)


def build_pipeline(model):
    """
    Chain two steps into one object: first scale the features, then apply the model.

    StandardScaler rescales every feature to mean 0 and standard deviation 1, so a feature
    with big numbers (BMI, up to 98) doesn't outweigh one with small numbers (0/1 answers).

    Because the scaler is inside the pipeline, calling pipeline.fit(X_train, y_train) learns the
    scaling from the training data ONLY. The test data is then scaled with those same numbers,
    which prevents data leakage.
    """
    return Pipeline([
        ("scaler", StandardScaler()),
        ("model", model),
    ])

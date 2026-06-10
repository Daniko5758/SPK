"""
Utility: Decision Tree Path Walker
Ekstrak path keputusan dari root ke leaf node untuk input tertentu.
Ini digunakan untuk menampilkan animated walk di visualisasi.
"""

import numpy as np
import os

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')


def load_feature_names():
    """Load feature names"""
    import json
    with open(os.path.join(MODELS_DIR, 'feature_names.json'), 'r') as f:
        return json.load(f)


def get_decision_path(model, X_input_array, raw_input=None):
    """
    Ekstrak node-node yang dilalui input melalui decision tree.

    Args:
        model: trained DecisionTreeClassifier
        X_input_array: numpy array input (1D atau 2D shape: (1, n_features))
        raw_input: optional dict dengan input asli user untuk label cleaner

    Returns:
        dict dengan informasi path: {
            'nodes': [node_id, ...],
            'features': [feature_name, ...],
            'thresholds': [threshold_value, ...],
            'directions': ['left'/'right', ...],
            'values': [input_value, ...],
            'comparisons': ['value <= threshold', ...]
        }
    """
    feature_names = load_feature_names()

    # Ensure 2D array
    if len(X_input_array.shape) == 1:
        X_input_array = X_input_array.reshape(1, -1)

    # Get decision path
    node_indicator = model.decision_path(X_input_array)
    node_indices = node_indicator.indices  # indices of nodes visited

    tree = model.tree_
    feature_idx = tree.feature
    threshold = tree.threshold

    steps = []
    leaf_node = None
    for node_id in node_indices:
        if feature_idx[node_id] != -2:  # -2 means LEAF
            feat_index = int(feature_idx[node_id])
            feat_name = feature_names[feat_index]
            thresh = float(threshold[node_id])
            input_val = float(X_input_array[0, feat_index])

            # Tentukan arah (kiri = <= threshold, kanan = > threshold)
            direction = 'left' if input_val <= thresh else 'right'

            # Coba gunakan raw_input untuk display lebih readable
            if raw_input and feat_name in raw_input:
                display_val = raw_input[feat_name]
            else:
                display_val = input_val

            comparison = f"{display_val} <= {thresh:.2f}"
            steps.append({
                'step': len(steps) + 1,
                'node_id': int(node_id),
                'feature': feat_name,
                'threshold': round(thresh, 2),
                'input_value': input_val,
                'display_value': display_val,
                'direction': direction,
                'comparison': comparison,
                'is_leaf': False
            })
        else:
            # Leaf node
            leaf_node = int(node_id)

    # Get leaf info
    last_node = node_indices[-1]
    class_probs = tree.value[last_node][0]
    sample_sum = float(np.sum(class_probs))
    predicted_class = int(np.argmax(class_probs))
    confidence = float(class_probs[predicted_class]) / sample_sum  # proporsi, bukan jumlah sample

    # Add leaf node as last step
    steps.append({
        'step': len(steps) + 1,
        'node_id': last_node,
        'feature': None,
        'threshold': None,
        'input_value': None,
        'direction': None,
        'comparison': None,
        'is_leaf': True,
        'predicted_class': predicted_class,
        'confidence': confidence,
        'class_probs': class_probs.tolist()
    })

    return {
        'steps': steps,
        'leaf_node': last_node,
        'predicted_class': predicted_class,
        'confidence': confidence,
        'class_probs': class_probs.tolist()
    }


def build_tree_structure(model, feature_names=None):
    """
    Bangun struktur tree lengkap untuk visualisasi.
    Mengembalikan nested dictionary representing the tree.

    Args:
        model: trained DecisionTreeClassifier
        feature_names: list nama fitur

    Returns:
        list of node dicts untuk visualisasi
    """
    if feature_names is None:
        feature_names = load_feature_names()

    tree = model.tree_
    nodes = []

    n_nodes = tree.node_count

    for node_id in range(n_nodes):
        feat_idx = int(tree.feature[node_id])
        thresh = float(tree.threshold[node_id])

        if feat_idx == -2:  # Leaf node
            values = tree.value[node_id][0]
            predicted_class = int(np.argmax(values))
            confidence = float(np.max(values))
            nodes.append({
                'id': node_id,
                'is_leaf': True,
                'predicted_class': predicted_class,
                'confidence': confidence,
                'samples': int(sum(values)),
                'class_distribution': values.tolist()
            })
        else:
            feat_name = feature_names[feat_idx]
            nodes.append({
                'id': node_id,
                'is_leaf': False,
                'feature': feat_name,
                'threshold': round(thresh, 2),
                'left_child': int(tree.children_left[node_id]),
                'right_child': int(tree.children_right[node_id])
            })

    return nodes


def get_tree_depth(model):
    """Get maximum depth of tree"""
    return model.get_depth()


def get_leaf_prediction(model, X_input_array):
    """Get prediction and probabilities for input"""
    pred = model.predict(X_input_array)[0]
    proba = model.predict_proba(X_input_array)[0]
    return int(pred), proba.tolist()
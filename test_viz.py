from utils.tree_walker import get_decision_path
from utils.visualizer_v2 import plot_decision_path_only
import joblib, numpy as np, json, matplotlib.pyplot as plt

base_tree = joblib.load('models/base_tree.joblib')
with open('models/label_mappings.json') as f:
    rm = json.load(f)['reverse_maps']

X = np.array([[45.0, 8.0, 5.0, 7.0, 25.0, 1.0, 1.0]])
path = get_decision_path(base_tree, X)
print("Steps:", len(path['steps']))
for s in path['steps']:
    if s['is_leaf']:
        print(f"  step {s['step']}: LEAF pred={s['predicted_class']} conf={s['confidence']:.2f}")
    else:
        print(f"  step {s['step']}: {s['feature']} thr={s['threshold']:.2f} val={s['input_value']} dir={s['direction']} leaf={s['is_leaf']}")

fig = plot_decision_path_only(path, rm)
plt.savefig('test_path_new.png', dpi=80, bbox_inches='tight')
plt.close()
print("OK - Figure saved to test_path_new.png")
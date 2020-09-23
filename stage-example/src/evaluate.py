import sys
import os
import pickle
import json

from sklearn.metrics import precision_recall_curve
import sklearn.metrics as metrics

# src/evaluate.py model.pkl data/features scores.json prc.json
if len(sys.argv) != 5:
    sys.stderr.write('Arguments error. Usage:\n')
    sys.stderr.write('\tpython evaluate.py model features scores plots\n')
    sys.exit(1)

model_file = sys.argv[1] # model.pkl
matrix_file = os.path.join(sys.argv[2], 'test.pkl') # data/features
scores_file = sys.argv[3] # scores.json
plots_file = sys.argv[4] # prc.json

with open(model_file, 'rb') as fd:
    model = pickle.load(fd)

with open(matrix_file, 'rb') as fd:
    matrix = pickle.load(fd)

labels = matrix[:, 1].toarray()
x = matrix[:, 2:]

predictions_by_class = model.predict_proba(x)
predictions = predictions_by_class[:, 1]

precision, recall, thresholds = precision_recall_curve(labels, predictions)

auc = metrics.auc(recall, precision)

with open(scores_file, 'w') as fd:
    json.dump({'auc': auc}, fd)

with open(plots_file, 'w') as fd:
    json.dump({'prc': [{
            'precision': p,
            'recall': r,
            'threshold': t
        } for p, r, t in zip(precision, recall, thresholds)
    ]}, fd)

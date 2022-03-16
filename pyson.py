import json
import itertools

run = {'sim': [{'model': ['Nakazato_2013'],
                'progenitor': [{'mass': 13,
                                'metal': 0.02,
                                't_rev': 100},
                               {'mass': 20,
                                'metal': 0.02,
                                't_rev': 100}]},
               {'model': ['Fornax_2021'],
                'progenitor': [{'mass': 13},
                               {'mass': 20}]}],
       'distance': [5, 10],
       'transform': ['NoTransformation'],
       'target': ['kamland']}

run2 = {'sim': [{'model': ['Nakazato_2013'],
                'progenitor': [{'mass': 20, 'metal': 0.02, 't_rev': 100}]}],
        'distance': [5.0],
        'transform': ['NoTransformation'],
        'target': ['kamland']}

file = 'pyson.json'

with open(file, 'w') as f:
    f.write(json.dumps(run, indent=2))

with open(file, 'r') as f:
    read = json.load(f)

sims = []
for s in read['sim']:
    [sims.append(p) for p in itertools.product(s['model'], s['progenitor'])]

params = itertools.product(read['distance'], read['transform'], read['target'])

coms = itertools.product(sims, params)
print("model, progenitor, distance, transform, target")
for i, com in enumerate(coms):
    c = f"{com[0][0]}, {com[0][1]}, {com[1][0]}, {com[1][1]}, {com[1][2]}"
    print(c)

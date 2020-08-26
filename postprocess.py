import json
import sys

import networkx as nx


def make_graph(data_as_list_of_dicts):
    invalid_tracker = set()
    for datapoint in data_as_list_of_dicts:
        label = datapoint.get("label")
        left = datapoint.get("left")
        right = datapoint.get("right")
        if label is None or label == -1 or label == 2 or left == right:
            invalid_tracker.add(frozenset({left, right}))

    graph = nx.DiGraph()
    for i, datapoint in enumerate(data_as_list_of_dicts):
        label = datapoint.get("label")
        left = datapoint.get("left")
        right = datapoint.get("right")
        if {left, right} in invalid_tracker:
            continue
        if label == 0:
            min_key, max_key = sorted([left, right])
            new_label = 0 if left == min_key else 1
            graph.add_edge(left, right, min_key=min_key, max_key=max_key, label=new_label)
        elif label == 1:
            min_key, max_key = sorted([left, right])
            new_label = 1 if left == min_key else 0
            graph.add_edge(right, left, min_key=min_key, max_key=max_key, label=new_label)
    return graph


def formatted_cycle(cycle):
    cycle_without_redundant = [str(edge[0]) for edge in cycle]
    cycle_without_redundant.append(str(cycle[0][0]))
    formatted = " -> ".join(cycle_without_redundant)
    return(formatted)


with open(sys.argv[1]) as f:
    data_as_list_of_dicts = json.load(f)

num_edges_total = len(data_as_list_of_dicts)
graph = make_graph(data_as_list_of_dicts)
num_edges_without_ambiguous = graph.number_of_edges()

num_direct_contradictions = 0
num_indirect_contradictions = 0
while not nx.is_directed_acyclic_graph(graph):
    cycle = nx.find_cycle(graph)
    cycle_string = formatted_cycle(cycle)
    print("Cycle found:", cycle_string)
    if len(cycle) == 2:
        num_direct_contradictions += 1
    else:
        num_indirect_contradictions += 1
    graph.remove_edges_from(cycle)

num_edges_without_ambiguous_and_cycles = graph.number_of_edges()
print(num_edges_without_ambiguous_and_cycles)
print(graph.number_of_edges())

print("\n#edges total:", num_edges_total)
print("#edges without ambiguous:", num_edges_without_ambiguous)
print("#edges without ambiguous and without cycles:",
      num_edges_without_ambiguous_and_cycles)
print("#direct contradictions:", num_direct_contradictions)
if num_indirect_contradictions == 0:
    print("\nNo cycles apart from direct contradictions (a>b & b>a) found.")
else:
    print("#indirect contradictions:", num_indirect_contradictions)

postprocessed_data_as_list_of_dicts = [
    {
        "left": data["min_key"],
        "right": data["max_key"],
        "label": data["label"]
    }
    for _, _, data in graph.edges(data=True)
]

postprocessed_data_as_list_of_dicts.sort(key=lambda x: x["right"])
postprocessed_data_as_list_of_dicts.sort(key=lambda x: x["left"])

with open(sys.argv[1][:-5] + "_postprocessed.json", "w") as f:
    json.dump(postprocessed_data_as_list_of_dicts, f)

import json
import sys

import networkx as nx


def edge_list(data_as_list_of_dicts):
    edge_list = []
    invalid_tracker = set()
    for datapoint in data_as_list_of_dicts:
        label = datapoint.get("label")
        left = datapoint.get("left")
        right = datapoint.get("right")
        is_duplicate_of_invalid = {left, right} in invalid_tracker
        if label is None or label == -1 or label == 2 or left == right or is_duplicate_of_invalid:
            invalid_tracker.add(frozenset({left, right}))
            continue
        if label == 0:
            edge_list.append((left, right))
        elif label == 1:
            edge_list.append((right, left))
    return edge_list


def formatted_cycle(cycle):
    cycle_without_redundant = [str(edge[0]) for edge in cycle]
    cycle_without_redundant.append(str(cycle[0][0]))
    formatted = " -> ".join(cycle_without_redundant)
    return(formatted)


graph = nx.DiGraph()
with open(sys.argv[1]) as f:
    data_as_list_of_dicts = json.load(f)

num_edges_total = len(data_as_list_of_dicts)
edge_list = edge_list(data_as_list_of_dicts)
graph.add_edges_from(edge_list)
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

print()
print("#edges total:", num_edges_total)
print("#edges without ambiguous:", num_edges_without_ambiguous)
print("#edges without ambiguous and without cycles:",
      num_edges_without_ambiguous_and_cycles)
print("#direct contradictions:", num_direct_contradictions)
if num_indirect_contradictions == 0:
    print()
    print("No cycles apart from direct contradictions (a>b & b>a) found.")
else:
    print("#indirect contradictions:", num_indirect_contradictions)

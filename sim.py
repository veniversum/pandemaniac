'''
The MIT License (MIT)

Copyright (c) 2013-2014 California Institute of Technology

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

__author__ = "Angela Gong (anjoola@anjoola.com)"

USAGE = '''
===========
   USAGE
===========

>>> import sim
>>> sim.run([graph], [dict with keys as names and values as a list of nodes])

Returns a dictionary containing the names and the number of nodes they got.

Example:
>>> graph = {"2": ["6", "3", "7", "2"], "3": ["2", "7, "12"], ... }
>>> nodes = {"strategy1": ["1", "5"], "strategy2": ["5", "23"], ... }
>>> sim.run(graph, nodes)
>>> {"strategy1": 243, "strategy6": 121, "strategy2": 13}

Possible Errors:
- KeyError: Will occur if any seed nodes are invalid (i.e. do not exist on the
            graph).
'''

from collections import Counter, OrderedDict
from copy import deepcopy
from random import randint


def run(adj_list, node_mappings):
  """
  Function: run
  -------------
  Runs the simulation on a graph with the given node mappings.

  adj_list: A dictionary representation of the graph adjacencies.
  node_mappings: A dictionary where the key is a name and the value is a list
                 of seed nodes associated with that name.
  """
  results = run_simulation(adj_list, node_mappings)
  return results


def run_simulation(adj_list, node_mappings):
  """
  Function: run_simulation
  ------------------------
  Runs the simulation. Returns a dictionary with the key as the "color"/name,
  and the value as the number of nodes that "color"/name got.

  adj_list: A dictionary representation of the graph adjacencies.
  node_mappings: A dictionary where the key is a name and the value is a list
                 of seed nodes associated with that name.
  """
  # Stores a mapping of nodes to their color.
  node_color = dict([(node, None) for node in adj_list.keys()])
  init(node_mappings, node_color)
  generation = 1

  # Keep calculating the epidemic until it stops changing. Randomly choose
  # number between 100 and 200 as the stopping point if the epidemic does not
  # converge.
  prev = None
  nodes = adj_list.keys()
  while not is_stable(generation, randint(100, 200), prev, node_color):
    prev = deepcopy(node_color)
    for node in nodes:
      (changed, color) = update(adj_list, prev, node)
      # Store the node's new color only if it changed.
      if changed: node_color[node] = color
    # NOTE: prev contains the state of the graph of the previous generation,
    # node_colros contains the state of the graph at the current generation.
    # You could check these two dicts if you want to see the intermediate steps
    # of the epidemic.
    generation += 1

  return get_result(node_mappings.keys(), node_color)


def init(color_nodes, node_color):
  """
  Function: init
  --------------
  Initializes the node to color mappings.
  """
  for (color, nodes) in color_nodes.items():
    for node in nodes:
      if node_color[node] is not None:
        node_color[node] = "__CONFLICT__"
      else:
        node_color[node] = color
  for (node, color) in node_color.items():
    if color == "__CONFLICT__":
      node_color[node] = None


def update(adj_list, node_color, node):
  """
  Function: update
  ----------------
  Updates each node based on its neighbors.
  """
  neighbors = adj_list[node]
  colored_neighbors = filter(None, [node_color[x] for x in neighbors])
  team_count = Counter(colored_neighbors)
  if node_color[node] is not None:
    team_count[node_color[node]] += 1.5
  most_common = team_count.most_common(1)
  if len(most_common) > 0 and \
    most_common[0][1] > len(colored_neighbors) / 2.0:
    return (True, most_common[0][0])

  return (False, node_color[node])


def is_stable(generation, max_rounds, prev, curr):
  """
  Function: is_stable
  -------------------
  Checks whether or not the epidemic has stabilized.
  """
  if generation <= 1 or prev is None:
    return False
  if generation == max_rounds:
    return True
  for node, color in curr.items():
    if not prev[node] == curr[node]:
      return False
  return True


def get_result(colors, node_color):
  """
  Function: get_result
  --------------------
  Get the resulting mapping of colors to the number of nodes of that color.
  """
  color_nodes = {}
  for color in colors:
    color_nodes[color] = 0
  for node, color in node_color.items():
    if color is not None:
      color_nodes[color] += 1
  return color_nodes


if __name__ == '__main__':
  print USAGE

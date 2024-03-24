# Stolen from homework bud made changes to use better distance modifiers.
import sys

def print_result(previous_nodes, shortest_path, start_node, target_node):
    path = []
    node = target_node
    
    while node != start_node:
        path.append(node)
        node = previous_nodes[node]
 
    # Add the start node manually
    path.append(start_node)
    
    print("We found the following best path with a value of {}.".format(shortest_path[target_node]))
    print(path)


def heuristic(node1, node2):
    # manhattan distance
    # keeping mahattan because it makes more sense with how pacman moves
    return abs(node1[0] - node2[0]) + abs(node1[1] - node2[1])


def dijkstra_or_a_star(nodes, start_node,goal_node, a_star=False):
    unvisited_nodes = list(nodes.costs)
    shortest_path = {}
    previous_nodes = {}

    max_value = sys.maxsize
    for node in unvisited_nodes:
        shortest_path[node] = max_value
    shortest_path[start_node] = 0

    while goal_node in unvisited_nodes:
        current_min_node = None
        for node in unvisited_nodes:
            if current_min_node == None:
                current_min_node = node
            elif shortest_path[node] < shortest_path[current_min_node]:
                current_min_node = node

        neighbors = nodes.getNeighbors(current_min_node)
        for neighbor in neighbors:            
            if a_star:
                tentative_value = shortest_path[current_min_node] + heuristic(current_min_node,neighbor)
            else:
                tentative_value = shortest_path[current_min_node] + nodes.nodesLUT[neighbor].neighborslength[nodes.getDirection(current_min_node,neighbor)]
            if tentative_value < shortest_path[neighbor]:
                shortest_path[neighbor] = tentative_value
                # We also update the best path to the current node
                previous_nodes[neighbor] = current_min_node
 
        # After visiting its neighbors, we mark the node as "visited"
        unvisited_nodes.remove(current_min_node)
    return previous_nodes, shortest_path
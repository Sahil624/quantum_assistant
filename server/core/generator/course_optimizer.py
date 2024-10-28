from functools import lru_cache
import json
from collections import defaultdict, deque
from typing import Dict, List, Tuple, TypeAlias

from .util import print_dp_matrix
from user_course.metastore import get_all_cells, get_cell_meta

graphType: TypeAlias = Dict[str, List[str]]


def parse_json_data(json_file):
    """Parse the JSON file containing course data."""
    with open(json_file, "r") as f:
        return json.load(f)


def build_prerequisite_graph() -> graphType:
    """Build a graph representing prerequisite relationships between learning objects."""
    graph = defaultdict(list)
    for cell in get_all_cells().values():
        cell_id = cell["cell_ID"]
        prereqs = cell.get("cell_prereqs", [])
        for prereq in prereqs:
            graph[cell_id].append(prereq)
    return graph


def get_lo_time(lo_id):
    """Get the estimated time for a learning object."""
    for cell in get_all_cells().values():
        if cell["cell_ID"] == lo_id:
            return int(cell["cell_estimated_time"])
    return 0


def get_topological_order(graph: graphType, selected_los: List[str]):
    in_degree_graph = defaultdict(list)
    in_degree = defaultdict(int)
    all_los = []
    pending_los = list(selected_los)

    while pending_los:
        lo = pending_los.pop(0)

        if lo in all_los:
            continue

        all_los.append(lo)

        for pre_req in graph[lo]:
            if pre_req not in all_los:
                pending_los.append(pre_req)

    for lo in all_los:
        if lo not in in_degree:
            in_degree[lo] = 0
        for prereq in graph[lo]:
            in_degree_graph[prereq].append(lo)
            in_degree[lo] += 1

    # Topological sort
    queue = deque(filter(lambda x: in_degree[x] == 0, in_degree.keys()))
    topological_order = []
    while queue:
        course_id = queue.popleft()
        topological_order.append(course_id)
        for neighbor in in_degree_graph[course_id]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    print(topological_order)

    return topological_order


def identify_prerequisite_chains(graph: graphType, selected_los: List[str]):
    """Identify all prerequisite chains in the graph."""
    # chains = []
    # visited = set()

    # def dfs(node, current_chain):
    #     if node in visited:
    #         return
    #     visited.add(node)
    #     current_chain.append(node)
    #     if not graph[node]:
    #         chains.append(list(current_chain))
    #     for prereq in graph[node]:
    #         dfs(prereq, current_chain)
    #     current_chain.pop()

    # for node in graph.copy():
    #     if node not in visited:
    #         dfs(node, [])

    # return chains

    chains = []

    def dfs(node, current_chain, visited):
        if node in visited:
            return
        visited.add(node)
        current_chain.append(node)
        if not graph[node]:
            chains.append(list(current_chain))
        for prereq in graph[node]:
            dfs(prereq, current_chain, visited)
        current_chain.pop()

    for lo in selected_los:
        dfs(lo, [], set())

    return chains


def dynamic_weight_knapsack_dp_optimized(
    items: List[Dict], capacity: int, weight_function
):
    n = len(items)

    # Use bitwise operations for state representation
    @lru_cache(maxsize=None)
    def calculate_weight(state: int, item_index: int) -> int:
        return weight_function(
            items[item_index], [items[j] for j in range(n) if state & (1 << j)]
        )

    # Initialize DP table
    dp = {0: [0] * (capacity + 1)}

    for i in range(n):
        new_dp = {}
        for state, values in dp.items():
            # Don't include the current item
            new_dp[state] = values.copy()

            # Try to include the current item
            new_state = state | (1 << i)
            if new_state not in new_dp:
                new_dp[new_state] = [float("-inf")] * (capacity + 1)

            actual_weight = calculate_weight(state, i)

            for w in range(capacity + 1):
                if values[w] == float("-inf"):
                    continue

                if w + actual_weight <= capacity:
                    new_value = values[w] + items[i]["value"]
                    new_dp[new_state][w + actual_weight] = max(
                        new_dp[new_state][w + actual_weight], new_value
                    )

        # Prune states
        dp = {k: v for k, v in new_dp.items() if max(v) > 0}

    # Find the maximum value and the corresponding state
    max_value = 0
    best_state = 0
    for state, values in dp.items():
        state_max = max(values)
        if state_max > max_value:
            max_value = state_max
            best_state = state

    # Convert best_state back to a list of indices
    selected_items = [i for i in range(n) if best_state & (1 << i)]

    return max_value, selected_items


def knapsack_optimize(
    chain_info: List[Tuple],
    topological_order: List[str],
    total_time: int,
    known_topics: int,
):
    dp = [[0] * (total_time + 1) for _ in range(len(topological_order) + 1)]
    for i in range(1, len(topological_order) + 1):
        lo_id = topological_order[i - 1]
        lo_time = get_lo_time(lo_id)

        # TODO: Verify this logic. Not sure about this once.
        # Basically if there is a course which is not reachable by any edge (i.e. not a pre-req for any)
        # Include it or not.
        # For now, I am only generating graph with relevant modules. But in future can generate course for all modules on startup.
        # Prioritize Leaf nodes (i.e. full chain is completed)
        course_value = 5 if any([chain[0][-1] == lo_id for chain in chain_info]) else 1

        for t in range(total_time + 1):
            is_known_topic = lo_id in known_topics
            # We can select a topic if
            # 1) It is not an already known topic.
            # 2) There is time to adjust it.
            # 3) It's pre reqs are processed.
            if not is_known_topic and (
                lo_time
                <= t
                # and all(
                #     prereq in set(topological_order[: i - 1])
                #     for prereq in lo["prerequisites"]
                # )
            ):
                dp[i][t] = max(dp[i - 1][t], dp[i - 1][t - lo_time] + course_value)
            else:
                dp[i][t] = dp[i - 1][t]

    # print_dp_matrix(dp, [i for i in range(total_time + 1)], topological_order)

    # Backtrack to find selected courses
    selected_los = []
    t = total_time
    for i in range(len(topological_order), 0, -1):
        # If these values are different, it means that including the i-th course improved
        # the solution for time t, so we include this course in our selection.
        if dp[i][t] != dp[i - 1][t]:
            lo_id = topological_order[i - 1]
            selected_los.append(lo_id)
            t -= get_lo_time(lo_id)
            print(f"Added course {lo_id}. Remaining time: {t}")
        else:
            print(
                f"Skipped course {topological_order[i-1]}. Not optimal for remaining time: {t}"
            )

    selected_los.reverse()  # Reverse to get courses in order of selection

    return selected_los


def optimize_lo_selection(selected_los: List[str], graph: graphType, time_limit: int):
    """
    Optimize the selection of learning objects within the time limit,
    considering prerequisite chains and using dynamic programming.
    """
    chains = identify_prerequisite_chains(graph, selected_los)
    topological_order = get_topological_order(graph, selected_los)
    # Calculate the time and value for each chain

    # print("======== LO Time ========")
    chain_info = []
    for chain in chains:
        # for lo in chain:
        # print(f'{lo} -> {get_lo_time(lo)}')
        chain_time = sum(get_lo_time(lo) for lo in chain)
        chain_value = sum(1 for lo in chain if lo in selected_los)
        chain_info.append((chain, chain_time, chain_value))

    # Sort chains by value-to-time ratio
    chain_info.sort(key=lambda x: x[2] / (x[1] or 1), reverse=True)
    # print("======================")

    print("==== Chains Info ====")
    for chain in chain_info:
        print(f"Chain '{chain[0]}' Time '{chain[1]}' Value '{chain[2]}'")
    print("======================")

    # def weight_function(item, current_items):
    #     # If a qualifying item is in the knapsack, reduce weight by 20%
    #     # if any(i.get('qualifier') for i in current_items):
    #     #     return item['base_weight'] * 0.8
    #     satisfied = []
    #     s_sum = 0
    #     # print('Item', item['name'])
    #     for lo in item["chain"]:
    #         for i in current_items:
    #             # print("C", i)
    #             # print('lo', lo)
    #             if lo in i["chain"] and lo not in satisfied:
    #                 satisfied.append(lo)
    #                 s_sum += get_lo_time(lo)
    #                 break
    #     # print("Satisfied", satisfied, s_sum)
    #     return item["base_weight"] - s_sum

    # items = []

    # for idx, chain in enumerate(chain_info):
    #     items.append(
    #         {"name": idx, "base_weight": chain[1], "value": 1, "chain": chain[0]}
    #     )

    # # print(items)

    # max_value, selected_items = dynamic_weight_knapsack_dp_optimized(
    #     items, time_limit, weight_function
    # )
    # cell_ids = [items[i]["chain"] for i in selected_items]
    cell_ids = knapsack_optimize(chain_info, topological_order, time_limit, [])

    for idx, chain in enumerate(chain_info):
        if not all([c in cell_ids for c in chain[0]]):
            print(f"Chain #{idx} not Satisfied. Starting '{chain[0][0]}'")

    return cell_ids


def main(selected_los, time_limit):
    """
    Main function to select learning objects within a given time limit,
    optimizing for prerequisite chains.
    """
    # data = parse_json_data(json_file)
    graph = build_prerequisite_graph()
    final_los = optimize_lo_selection(set(selected_los), graph, time_limit)
    return final_los

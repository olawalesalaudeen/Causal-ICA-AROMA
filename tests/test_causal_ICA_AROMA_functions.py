import unittest

import networkx as nx

from causal_ica_aroma.causal_ICA_AROMA_functions import get_updated_motion_ICs


class TestCausalICAAROMAFuncs(unittest.TestCase):

    def test_get_updated_motion_ICs_all_parents_aroma_motion(self):
        causal_criterion = "all_parents_aroma_motion"

        # Define motion_ics as a deterministic subset of nodes
        aroma_motion_ICs = [0, 1, 2, 10]

        # Generate a directed graph
        G = nx.DiGraph()
        edges = [
            (0, 3),  # Node 3 has all parents in aroma_motion_ICs
            (1, 3),
            (2, 3),
            (10, 6),  # Node 6 has all parents in aroma_motion_ICs
            (4, 5),  # Node 5 has only a subset of parents in aroma_motion_ICs
            (6, 5),
            (10, 5),
            (7, 8),  # Additional sparse edges
            (19, 8),
            (18, 19),
            (19, 20),
            (30, 31),
        ]
        G.add_edges_from(edges)

        # Expected updated motion ICs
        expected_motion_ICs = aroma_motion_ICs + [3, 6]
        expected_motion_ICs.sort()

        # Updated motion ICs
        updated_motion_ICs = get_updated_motion_ICs(
            G, causal_criterion, aroma_motion_ICs
        )

        print(expected_motion_ICs)
        print(updated_motion_ICs)
        # Check that all motion_ICs are included in the updated list
        self.assertTrue(updated_motion_ICs == expected_motion_ICs)


if __name__ == "__main__":
    unittest.main()

import time
import unittest
import random
import string
from ete3 import Tree
from project_overbooking import ProjectTree
from project_overbooking import db


CYCLES = 100


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


class PerformanceTestCase(unittest.TestCase):
    def setUp(self):
        db.reset()

    def _test_run(self, num, cycles):
        root = Tree()
        root.populate(num)
        for leaf in root.traverse():
            if leaf.name == '':
                leaf.name = randomword(10)
            leaf.dist = 10
            leaf.limits = {'vm': leaf.dist}

        leaf, _ = root.get_farthest_leaf()
        f = open('po_perf_%s' % num, 'w')
        db.save_projects(ProjectTree(root))
        for i in range(cycles):
            db_start = time.time()
            db_tree = db.load_projects()
            f.write('db %f\n' % (time.time() - db_start))
            tree_start = time.time()
            tree = ProjectTree(db_tree)
            f.write('tree %f\n' % (time.time() - tree_start))
            tree.use(leaf.name, {'vm': 10})

    def test_10(self):
        self._test_run(10, CYCLES)

    def test_100(self):
        self._test_run(100, CYCLES)

    def test_1000(self):
        self._test_run(1000, CYCLES)

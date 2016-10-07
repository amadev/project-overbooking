import unittest
from project_overbooking import ProjectTree, ProjectLimitExceed


class ProjectTestCase(unittest.TestCase):
    def test_simple_overbooking_work(self):
        tree = ProjectTree().load("(b:10,c:10,d:20)a:40;")
        tree.use('b', 11)

    def test_fail_if_overbooking_disabled_on_leaf(self):
        tree = ProjectTree().load(
            "(b:10,c:10,d:20)a:40;",
            properties={'b': {'overbooking_allowed': False}})
        tree.use('b', 5)
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', 6)

    def test_fail_if_sibling_eat_all(self):
        tree = ProjectTree().load("(b:10,c:10,d:20)a:40;")
        tree.use('c', 40)
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', 1)

import unittest
from project_overbooking import ProjectTree, ProjectLimitExceed


class ProjectTestCase(unittest.TestCase):
    def test_simple_overbooking_work(self):
        properties = {}
        for node in ('a', 'b', 'c', 'd'):
            properties[node] = {'overbooking_allowed': True}
        tree = ProjectTree().load(
            "(b:10,c:10,d:20)a:40;", properties=properties)
        tree.use('b', 11)

    def test_fail_if_overbooking_disabled_on_leaf(self):
        tree = ProjectTree().load(
            "(b:10,c:10,d:20)a:40;")
        tree.use('b', 5)
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', 6)

    def test_fail_if_sibling_eat_all(self):
        tree = ProjectTree().load("(b:10,c:40,d:20)a:40;")
        tree.use('c', 40)
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', 1)

    def test_sb1(self):
        tree = ProjectTree().load(
            "((project1a: 7, project1b: 10)project0a:10,project0b:-1)domain:-1;")
        print tree.structure()
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project1a', tree.use, 'project1a', 8)
        tree.use('project1a', 7)
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project0a', tree.use, 'project1b', 4)
        tree.use('project1b', 3)

    def test_sb2(self):
        tree = ProjectTree().load(
            "((project1a: 7, project1b: -1)project0a:10,project0b:-1)domain:-1;")
        tree.save()
        print tree.structure()
        tree.use('project0a', 5)
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project0a', tree.use, 'project1a', 6)
        tree.use('project1a', 5)

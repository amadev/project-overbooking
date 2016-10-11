import unittest
from project_overbooking import ProjectTree, ProjectLimitExceed
from project_overbooking import db


class ProjectTestCase(unittest.TestCase):
    def test_simple_overbooking_work(self):
        properties = {}
        for node in ('a', 'b', 'c', 'd'):
            properties[node] = {'overbooking_allowed': True}
        tree = ProjectTree().load(
            "(b:10,c:10,d:20)a:40;", properties=properties)
        tree.use('b', {'vm': 11})

    def test_fail_if_overbooking_disabled_on_leaf(self):
        tree = ProjectTree().load(
            "(b:10,c:10,d:20)a:40;")
        tree.use('b', {'vm': 5})
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', {'vm': 6})

    def test_fail_if_sibling_eat_all(self):
        tree = ProjectTree().load("(b:10,c:40,d:20)a:40;")
        tree.use('c', {'vm': 40})
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', {'vm': 1})

    def test_sb1(self):
        tree = ProjectTree().load(
            "((project1a: 7, project1b: 10)project0a:10,project0b:-1)domain:-1;")
        print tree.structure()
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project1a', tree.use, 'project1a', {'vm': 8})
        tree.use('project1a', {'vm': 7})
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project0a', tree.use, 'project1b', {'vm': 4})
        tree.use('project1b', {'vm': 3})

    def test_sb2(self):
        tree = ProjectTree().load(
            "((project1a: 7, project1b: -1)project0a:10,project0b:-1)domain:-1;")
        tree.save()
        print tree.structure()
        tree.use('project0a', {'vm': 5})
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project0a', tree.use, 'project1a', {'vm': 6})
        tree.use('project1a', {'vm': 5})

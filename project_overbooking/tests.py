import unittest
from project_overbooking import ProjectTree, ProjectLimitExceed
from project_overbooking import db
from ete3 import Tree
from collections import OrderedDict


class ProjectTestCase(unittest.TestCase):

    def _get_tree(self, str, properties=None):
        root = Tree(str, format=1)
        for leaf in root.traverse():
            leaf.limits = {'vm': leaf.dist}
        print self._tree_structure(root)
        db.save_projects(ProjectTree(root))
        return ProjectTree(db.load_projects(), properties=properties)

    def _tree_structure(self, tree):
        return tree.get_ascii(
            attributes=["name", "dist"], show_internal=True)

    def test_simple_overbooking_work(self):
        properties = {}
        for node in ('a', 'b', 'c', 'd'):
            properties[node] = {'overbooking_allowed': True}
        tree = self._get_tree("(b:10,c:10,d:20)a:40;", properties)
        tree.use('b', {'vm': 11})

    def test_fail_if_overbooking_disabled_on_leaf(self):
        tree = self._get_tree("(b:10,c:10,d:20)a:40;")
        tree.use('b', {'vm': 5})
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', {'vm': 6})

    def test_fail_if_sibling_eat_all(self):
        tree = self._get_tree("(b:10,c:40,d:20)a:40;")
        tree.use('c', {'vm': 40})
        self.assertRaises(ProjectLimitExceed, tree.use, 'b', {'vm': 1})

    def test_fail_with_multiple_resources(self):
        tree = self._get_tree("(b:10,c:40,d:20)a:40;")
        for p in tree.projects.values():
            p.limit['mem'] = 10
            p.used['mem'] = 0
        def run():
            tree.use('c', OrderedDict((("vm", 40), ("mem", 20))))
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'Exceed in node c, resource mem', run)
        tree.projects['c'].limit['mem'] = 30
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'Exceed in node a, resource mem', run)

    def test_sb1(self):
        tree = self._get_tree(
            "((project1a: 7, project1b: 10)project0a:10,project0b:-1)domain:-1;")
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project1a', tree.use, 'project1a', {'vm': 8})
        tree.use('project1a', {'vm': 7})
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project0a', tree.use, 'project1b', {'vm': 4})
        tree.use('project1b', {'vm': 3})

    def test_sb2(self):
        tree = self._get_tree("((project1a: 7, project1b: -1)project0a:10,project0b:-1)domain:-1;")
        tree.use('project0a', {'vm': 5})
        self.assertRaisesRegexp(
            ProjectLimitExceed, 'project0a', tree.use, 'project1a', {'vm': 6})
        tree.use('project1a', {'vm': 5})

"""PoC of the project overbooking logic"""

from ete3 import Tree


class ProjectLimitExceed(Exception):
    pass


class Project(object):
    def __init__(
            self, leaf, limit, used=0, overbooking_allowed=False):
        self.leaf = leaf
        self.limit = limit
        self.used = used
        self.overbooking_allowed = overbooking_allowed

    def get_subproject_used(self):
        """Get sum of used resorces for all subtree"""
        used = 0
        for leaf in self.leaf.children:
            used += leaf.project.used + leaf.project.get_subproject_used()
        return used

    def parent(self):
        if self.leaf.up:
            return self.leaf.up.project
        return None

    def check_limit(self, value):
        self.used += value
        if self.limit == -1 or (
                self.used + self.get_subproject_used() <= self.limit):
            if self.parent():
                return self.parent().check_limit(0)
            return True
        else:
            if not self.overbooking_allowed:
                raise ProjectLimitExceed('Exceed in node %s' % self.leaf.name)
            else:
                if self.parent():
                    return self.parent().check_limit(0)
                raise ProjectLimitExceed('Exceed in node %s' % self.leaf.name)


class ProjectTree(object):
    def __init__(self):
        self.projects = {}
        self.tree = None

    def load(self, tree_string, properties={}):
        self.tree = Tree(tree_string, format=1)
        for leaf in self.tree.traverse():
            node_props = properties.get(leaf.name, {})
            self.projects[leaf.name] = Project(
                leaf, leaf.dist, **node_props)
            leaf.project = self.projects[leaf.name]
        return self

    def use(self, name, value):
        try:
            self.projects[name].check_limit(value)
        except ProjectLimitExceed:
            self.projects[name].used -= value
            raise

    def structure(self):
        return self.tree.get_ascii(
            attributes=["name", "dist"], show_internal=True)

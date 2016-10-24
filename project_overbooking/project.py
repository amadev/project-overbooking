"""PoC of the project overbooking logic"""
from collections import OrderedDict


class ProjectLimitExceed(Exception):
    pass


OVERBOOKING_ALLOWED = True


class QuotaNode(object):
    def __init__(
            self, name, limits, usages):
        self.name = name
        self.limits = limits
        self.usages = usages
        self.children = []
        self.parent = None

    def get_subproject_usages(self, resources):
        """Get sum of usages resources for all subtree"""
        usages = self.init_usages(resources)
        for node in self.children:
            sp_usages = node.get_subproject_usages(resources)
            for resource in resources:
                usages[resource] += (node.usages[resource] +
                                   sp_usages[resource])
        return usages

    def init_usages(self, resources):
        return {name: 0 for name in resources}

    def check(self, deltas):
        sp_usages = self.get_subproject_usages(deltas)
        for resource, value in deltas.items():
            self.usages[resource] += value
            total_usages = sp_usages[resource] + self.usages[resource]
            if (self.limits[resource] == -1 or
                    total_usages <= self.limits[resource]):
                if OVERBOOKING_ALLOWED and self.parent:
                    self.parent.check(self.init_usages(deltas))
                continue
            else:
                raise ProjectLimitExceed(
                    'Exceed in node %s, resource %s' % (
                        self.name, resource))
        return True


class ProjectTree(object):
    def __init__(self, root, properties=None):
        """
        root - tree like object with attributes required:
        - name
        - limits
        - children
        """
        self.projects = OrderedDict()
        if properties is None:
            properties = {}
        self.properties = properties
        self._load_tree(root)

    def _load_tree(self, node):
        if not self.projects:
            self._init_project(node)
        for leaf in node.children:
            self._init_project(leaf, self.projects[node.name])
            self.projects[node.name].children.append(
                self.projects[leaf.name])
            self._load_tree(leaf)

    def _init_project(self, node, parent=None):
        node_props = self.properties.get(node.name, {})
        node_props['limits'] = node.limits
        node_props['usages'] = {name: 0 for name in node.limits}
        self.projects[node.name] = QuotaNode(
            node.name, **node_props)
        self.projects[node.name].parent = parent

    def use(self, project, deltas):
        try:
            self.projects[project].check(deltas)
        except ProjectLimitExceed:
            for resource, value in deltas.items():
                self.projects[project].usages[resource] -= value
            raise

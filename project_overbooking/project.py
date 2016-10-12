"""PoC of the project overbooking logic"""
from collections import OrderedDict


class ProjectLimitExceed(Exception):
    pass


class Project(object):
    def __init__(
            self, node, limit, used=None, overbooking_allowed=False):
        self.node = node
        self.limit = limit
        if not used:
            used = self.init_used(limit)
        self.used = used
        self.overbooking_allowed = overbooking_allowed

    def get_subproject_used(self, resources):
        """Get sum of used resorces for all subtree"""
        used = self.init_used(resources)
        for node in self.node.children:
            sp_used = node.project.get_subproject_used(resources)
            for resource in resources:
                used[resource] += (node.project.used[resource] +
                                   sp_used[resource])
        return used

    def parent(self):
        if self.node.up:
            return self.node.up.project
        return None

    def init_used(self, resources):
        return {name: 0 for name in resources}

    def check_limit(self, resources):
        sp_used = self.get_subproject_used(resources)
        for resource, value in resources.items():
            self.used[resource] += value
            total_used = sp_used[resource] + self.used[resource]
            if (self.limit[resource] == -1 or
                    total_used <= self.limit[resource]):
                if self.parent():
                    self.parent().check_limit(self.init_used(resources))
                continue
            else:
                if not self.overbooking_allowed:
                    raise ProjectLimitExceed(
                        'Exceed in node %s, resource %s' % (
                            self.node.name, resource))
                else:
                    if self.parent():
                        self.parent().check_limit(self.init_used(resources))
                    else:
                        raise ProjectLimitExceed(
                            'Exceed in node %s, resource %s' % (
                                self.node.name, resource))
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
            self._init_project(leaf, node)
            self._load_tree(leaf)

    def _init_project(self, node, parent=None):
        node_props = self.properties.get(node.name, {})
        node_props['limit'] = node.limits
        self.projects[node.name] = Project(
            node, **node_props)
        node.project = self.projects[node.name]
        node.up = parent

    def use(self, project, resources):
        try:
            self.projects[project].check_limit(resources)
        except ProjectLimitExceed:
            for resource, value in resources.items():
                self.projects[project].used[resource] -= value
            raise

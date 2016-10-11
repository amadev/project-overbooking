"""PoC of the project overbooking logic"""

from ete3 import Tree
from project_overbooking import db


class ProjectLimitExceed(Exception):
    pass


class Project(object):
    def __init__(
            self, leaf, limit, used=None, overbooking_allowed=False):
        self.leaf = leaf
        self.limit = limit
        if not used:
            used = self.init_used(limit)
        self.used = used
        self.overbooking_allowed = overbooking_allowed

    def get_subproject_used(self, resources):
        """Get sum of used resorces for all subtree"""
        used = self.init_used(resources)
        for leaf in self.leaf.children:
            sp_used = leaf.project.get_subproject_used(resources)
            for resource in resources:
                used[resource] += leaf.project.used[resource] + sp_used[resource]
        return used

    def parent(self):
        if self.leaf.up:
            return self.leaf.up.project
        return None

    def init_used(self, resources):
        return {name: 0 for name in resources}

    def check_limit(self, resources):
        sp_used = self.get_subproject_used(resources)
        for resource, value in resources.items():
            self.used[resource] += value
            total_used = sp_used[resource] + self.used[resource]
            if self.limit[resource] == -1 or total_used <= self.limit[resource]:
                if self.parent():
                    return self.parent().check_limit(self.init_used(resources))
                return True
            else:
                if not self.overbooking_allowed:
                    raise ProjectLimitExceed(
                        'Exceed in node %s, resource %s' % (self.leaf.name, resource))
                else:
                    if self.parent():
                        return self.parent().check_limit(self.init_used(resources))
                    raise ProjectLimitExceed(
                        'Exceed in node %s, resource %s' % (self.leaf.name, resource))


class ProjectTree(object):
    def __init__(self):
        self.projects = {}
        self.tree = None

    def load(self, tree_string, properties={}):
        self.tree = Tree(tree_string, format=1)
        for leaf in self.tree.traverse():
            node_props = properties.get(leaf.name, {})
            self.projects[leaf.name] = Project(
                leaf, {'vm': leaf.dist}, **node_props)
            leaf.project = self.projects[leaf.name]
        return self

    def use(self, project, resources):
        try:
            self.projects[project].check_limit(resources)
        except ProjectLimitExceed:
            for resource, value in resources.items():
                self.projects[project].used[resource] -= value
            raise

    def structure(self):
        return self.tree.get_ascii(
            attributes=["name", "dist"], show_internal=True)

    def save(self):
        nodes = {}
        root = None
        for el in self.tree.traverse():
            parent = None
            if el.up:
                if el.up.name in nodes:
                    parent = nodes[el.up.name]
                else:
                    parent = db.Project(name=el.up.name)
                    nodes[el.up.name] = parent

            if el.name in nodes:
                project = nodes[el.name]
            else:
                project = db.Project(name=el.name, parent=parent)
                nodes[el.name] = project
            if not root:
                root = project
            quota = db.Quota(resource='vm', limit=el.dist, project=project)
            db.session.add(quota)
        db.session.add(root)
        db.session.commit()



def load_tree():
    projects = db.load_projects()
    dct = {}
    for project in projects:
        dct[project.name] = Project()

import os
from collections import defaultdict
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref, joinedload
from sqlalchemy.orm.attributes import set_committed_value


Base = declarative_base()


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, Sequence('project_id_seq'), primary_key=True)
    name = Column(String(50))
    parent_id = Column(Integer, ForeignKey('project.id'))
    quotas = relationship("Quota")
    usages = relationship("Usage")

    children = relationship(
        "Project", backref=backref("parent", remote_side=id))


class Quota(Base):
    __tablename__ = 'quota'
    id = Column(Integer, Sequence('quota_id_seq'), primary_key=True)
    resource = Column(String(50))
    limit = Column(Integer())
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship("Project")


class Usage(Base):
    __tablename__ = 'usage'
    id = Column(Integer, Sequence('usage_id_seq'), primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    value = Column(Integer())
    project = relationship("Project")


def save_projects(tree):
    nodes = {}
    root = None
    for p in tree.projects.values():
        el = p.node
        parent = None
        if el.up:
            if el.up.name in nodes:
                parent = nodes[el.up.name]
            else:
                parent = Project(name=el.up.name)
                nodes[el.up.name] = parent

        if el.name in nodes:
            project = nodes[el.name]
        else:
            project = Project(name=el.name, parent=parent)
            nodes[el.name] = project
        if not root:
            root = project
        quota = Quota(resource='vm', limit=el.dist, project=project)
        session.add(quota)
    session.add(root)
    session.commit()


def load_projects():
    projects = session.query(Project).options(
        joinedload('quotas')).all()

    root = None
    children = defaultdict(list)
    for project in projects:
        if project.parent:
            children[project.parent.id].append(project)
        if project.parent is None:
            root = project

    for project in projects:
        set_committed_value(project, 'children', children[project.id])
        project.limits = {
            quota.resource: quota.limit for quota in project.quotas}

    return root


def create_db(conn_str):
    engine = create_engine(conn_str, echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


session = create_db(os.environ.get('POB_CONN_STR', 'sqlite:///:memory:'))

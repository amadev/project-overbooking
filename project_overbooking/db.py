from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref


Base = declarative_base()


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, Sequence('project_id_seq'), primary_key=True)
    name = Column(String(50))
    parent_id = Column(Integer, ForeignKey('project.id'))
    quotas = relationship("Quota")
    usages = relationship("Usage")

    children = relationship("Project",
                            backref=backref("parent", remote_side=id))


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


engine = create_engine('sqlite:///:memory:', echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

from app import db, app
from mod_tags.models import *
from datetime import datetime
from helper_db import *
from sqlalchemy import extract
import pycountry

class Projects(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%r %r>' % (self.id, self.name)

class TS_Requests(db.Model):
    __tablename__ = 'ts_requests'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<%r %r>' % (self.id, self.name)

##########
# CREATE #
##########

def add_project(name):
    project_entry = Projects(
       name           = name
       )
    
    save_project = commit_entry(project_entry)
    return save_project

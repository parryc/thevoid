from app import db, app
from helper_db import *
from sqlalchemy import PrimaryKeyConstraint

class VPS_Requests(db.Model):
    __tablename__ = 'vps_requests'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Text)
    request_project_size = db.Column(db.Text)
    timeseries_has_response = db.Column(db.Boolean)
    timeseries_response = db.Column(db.Text)  # Comma delimited
    timeseries_interval_count = db.Column(db.Float)

    def __init__(self, request_id, request_project_size, timeseries_has_response, timeseries_response,
                 timeseries_interval_count):
        self.request_id = request_id
        self.request_project_size = request_project_size
        self.timeseries_has_response = timeseries_has_response
        self.timeseries_response = timeseries_response
        self.timeseries_interval_count = timeseries_interval_count

    def __repr__(self):
        return '<%r %r %r>' % (self.id, self.request_id, self.timeseries_has_response)

class Subprojects(db.Model):
    __tablename__ = 'subproject_hours_aggregates'

    subproject = db.Column(db.Text, primary_key=True)
    hours_aggregate = db.Column(db.Float)

    def __repr__(self):
        return '<%r %r>' % (self.subproject, self.hours_aggregate)

class Hours(db.Model):
    __tablename__ = 'hours_transactions'
    __table_args__ = (
        PrimaryKeyConstraint('log_date', 'integration'),
    )

    log_date = db.Column(db.Date)
    integration = db.Column(db.Text)
    hours_logged = db.Column(db.Float)

    def __repr__(self):
        return '<%s %s %s>' % (self.integration, self.log_date, self.hours_logged)

##########
# CREATE #
##########

def add_vps_request(request_id, request_project_size, timeseries_has_response, timeseries_response,
                timeseries_interval_count):
    request_entry = VPS_Requests(
        request_id = request_id
       ,request_project_size = request_project_size
       ,timeseries_has_response = timeseries_has_response
       ,timeseries_response = timeseries_response
       ,timeseries_interval_count = timeseries_interval_count
       )

    save_request = commit_entry(request_entry)
    return save_request


##########
# UPDATE #
##########

def edit_vps_request(request_id, timeseries_json):
    _request = get_vps_request(request_id)
    _request.timeseries_response = timeseries_json['df_output']['inline_data']
    _request.timeseries_has_response = True

    save_request = commit_entry(_request)
    return save_request


##########
#  GET   #
##########

def get_vps_request(request_id):
    return VPS_Requests.query.filter(VPS_Requests.request_id==request_id).first()

def get_subproject(subproject):
    return Subprojects.query.filter(Subprojects.subproject==subproject).first()

def get_hours(subproject):
    return Hours.query.filter(Hours.integration==subproject).all()

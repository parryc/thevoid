#!/usr/bin/env python
# coding: utf-8

from app import db

def commit_entry(entry):
  try:
    db.session.add(entry)
    db.session.commit()
    return {'status':True,'message':'Success','entry':entry}
  except Exception as e:
    error = str(e).split('.')[0]
    return {'status':False,'message':'Error: %s' % error, 'entry':None}

def delete_entry(entry):
  try:
    db.session.delete(entry)
    db.session.commit()
    return {'status':True,'message':'Success', 'entry':entry.id}
  except Exception as e:
    error = str(e).split('.')[0]
    return {'status':False,'message':'Error: %s' % error, 'entry':entry.id}

def get_counts(field):
  """ 
    Get count by field passed as input
    Ex. get_counts(Supersource.source_property)
    returns a list of tuples that are (field, count)
    e.g [(1, 14), (2, 3)] 
    (14 sources of property type 1, etc.)
  """
  return db.session.query(field,db.func.count(field)).group_by(field).all()

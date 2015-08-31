#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

mod_thebookofd = Blueprint('thebookofd', __name__)

localhost = 'localhost:5000'
prod = 'thebookofd.eu'

##########
# Routes #
##########


@mod_thebookofd.route('/', methods=['GET'], host='thebookofd.eu')
def index():
    return render_template('thebookofd/index.html')


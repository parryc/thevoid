#!/usr/bin/env python
# coding: utf-8
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash

mod_leflan = Blueprint('leflan', __name__)


##########
# Routes #
##########


@mod_leflan.route('/', methods=['GET'], host='leflan.eu')
def index():
    return render_template('leflan/index.html')


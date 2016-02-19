# -*- coding: utf-8 -*-
from flask import Blueprint
from .defender.androidRunner import AndroidRunner

main = Blueprint('main',__name__)

from . import deviceView,jobView,caseView,loginView,mirrorView

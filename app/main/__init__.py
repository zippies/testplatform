# -*- coding: utf-8 -*-
from flask import Blueprint
from .defender.androidRunner import AndroidRunner
from .defender.monkeyRunner import MonkeyRunner
from .defender.compatibleRunner import CompatibleRunner

main = Blueprint('main',__name__)

from . import deviceView,jobView,caseView,loginView,mirrorView,dataView

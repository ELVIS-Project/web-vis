#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           django-vis
# Program Description:    Web-based User Interface for vis
#
# Filename:               django-vis/__init__.py
# Purpose:                ????
#
# Copyright (C) 2013 Jamie Klassen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#--------------------------------------------------------------------------------------------------

# Ensure we can import "vis"
import imp
try:
    imp.find_module(u'vis')
except ImportError:
    import sys
    sys.path.insert(0, u'..')


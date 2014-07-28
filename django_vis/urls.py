#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           django-vis
# Program Description:    Web-based User Interface for vis
#
# Filename:               django-vis/urls.py
# Purpose:                URL patterns for the Counterpoint Web App
#
# Copyright (C) 2013, 2014 Jamie Klassen, Saining Li, and Christopher Antila
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
"URL patterns for the Counterpoint Web App"

# allow using 'urlpatterns' as a constant
# pylint: disable=invalid-name

from django.conf.urls import patterns, url
from django.conf import settings
#from django.conf.urls.static import static
from . import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$', views.MainView.as_view(), name='main'),
    url(r'^import/?$', views.import_files, name='import'),
    url(r'^experiment/?$', views.run_experiment, name='experiment'),
    url(r'^output/table/?$', views.output_table, name='table'),
    url(r'^output/graph/?$', views.output_graph, name='graph'),
    url(r'^upload/$', views.upload),
    url(r'^delete/$', views.delete),
    # url(r'^admin/', include(admin.site.urls)),
)
urlpatterns += patterns('',
                        (r'^media/(?P<path>.*)$',
                         'django.views.static.serve',
                         {'document_root': settings.MEDIA_ROOT}))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           django-vis
# Program Description:    Web-based User Interface for vis
#
# Filename:               django-vis/views.py
# Purpose:                Holds views for the Counterpoint Web App
#
# Copyright (C) 2013 to 2014 Jamie Klassen, Saining Li, and Christopher Antila
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
"Holds views for the Counterpoint Web App"

import os
import time
import ujson as json
from django.views import generic
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from jsonview import decorators
import settings
from vis.workflow import WorkflowManager

from django_vis.models import Piece, ResultLocation

@decorators.json_view
def import_files(request):
    """
    Called with the /api/import URL to load files into the WorkflowManager and return the metadata
    it discovers.
    """
    filepaths = [piece.file.path for piece in Piece.objects.filter(user_id=request.session.session_key)]
    workm = WorkflowManager(filepaths)
    workm.load('pieces')
    request.session['workm'] = workm
    return [
        {"Filename": os.path.basename(workm.metadata(i, 'pathname')),
         "Title": workm.metadata(i, 'title'),
         "Part Names": workm.metadata(i, 'parts'),
         "Offset": None,
         "Part Combinations": None,
         "Repeat Identical": False}
        for i in xrange(len(workm))
    ], 200

def save_results(user_id, pathname, result_type):
    """
    Given the user_id (session ID), pathname to a result, and the type of the result, save the
    result in the database. First, we delete all previous results of the same type for this user.
    """
    # delete previous table ResultLocation instances
    old_results = ResultLocation.objects.filter(user_id=user_id, result_type=result_type)
    for each_result in old_results:
        each_result.delete()
    # make a new table ResultLocation
    location = ResultLocation()
    location.user_id = user_id
    location.save()
    location.result_type = result_type
    location.save()
    if 'table' == result_type:
        location.pathname = pathname
        location.save()
    else:  # 'graph' == result_type
        splitted = pathname.split('/')
        location.pathname = '%s%s/%s' % (settings.MEDIA_URL, splitted[-2], splitted[-1])
        location.save()

@decorators.json_view
def run_experiment(request):
    """
    Called with the /api/experiment URL to run the analysis and prepare the output.
    """
    workm = request.session['workm']
    # Set metadata and settings
    updated_pieces = json.loads(request.GET['updated_pieces'])
    interval_quality = True if request.GET['quality'] == 'display' else False
    simple_intervals = True if request.GET['octaves'] == 'simple' else False
    for (i, piece) in enumerate(updated_pieces):
        workm.metadata(i, 'title', piece['title'])
        workm.metadata(i, 'parts', piece['partNames'])
        workm.settings(i, 'offset interval', None if piece['offset'] == '' else float(piece['offset']))
        workm.settings(i, 'voice combinations', piece['partCombinations'])
        workm.settings(i, 'filter repeats', piece['repeatIdentical'])
    workm.settings(None, 'interval quality', interval_quality)
    workm.settings(None, 'simple intervals', simple_intervals)
    # run experiment
    output = request.GET['output']
    if 'lilypond' == output:
        # output('LilyPond') requires not counting frequency
        workm.settings(None, 'count frequency', False)
    n = None if request.GET['n'] == '' else int(request.GET['n'])
    topx = None if request.GET['topx'] == '' else int(request.GET['topx'])
    threshold = None if request.GET['threshold'] == '' else int(request.GET['threshold'])

    if request.GET['experiment'] == 'interval n-grams':
        workm.settings(0, 'n', n)
        workm.run('interval n-grams')
    else:
        workm.run('intervals')

    # Produce Output
    # filename should be time-based, so users see less of a mess
    # TODO: this should really use the 'tempfile' module
    # TODO: I should also try to handle errors
    directory = os.path.join(settings.MEDIA_ROOT, request.session.session_key)
    if not os.path.exists(directory):
        os.mkdir(directory)
    elif not os.path.isdir(directory):
        os.remove(directory)
        os.mkdir(directory)

    filename = str(time.time()).replace('.', '')
    filename = os.path.join(directory, filename)

    rendered_paths = None

    if output == 'table':
        post = workm.export('HTML', '%s.html' % filename, top_x=topx, threshold=threshold)
        save_results(request.session.session_key, post, output)
    elif output == 'graph':
        post = workm.output('R histogram', '%s' % filename, top_x=topx, threshold=threshold)
        save_results(request.session.session_key, post, output)
    elif output == 'lilypond':
        paths = workm.output('LilyPond', filename, top_x=topx, threshold=threshold)

        # prepare the URLs we'll return
        rendered_paths = []
        for each in paths:
            rendered_paths.append('{}{}/{}.pdf'.format(settings.MEDIA_URL,
                                                       each.split('/')[-2],
                                                       each.split('/')[-1][:-3]))
    else:
        # no experiment was run
        pass  # TODO: return something not-200

    return {'type': output, 'rendered_paths': rendered_paths}, 200

def output_table(request):
    """
    Called with the /output/table URL to fetch a table.
    """
    location = ResultLocation.objects.filter(user_id=request.session.session_key, result_type='table')
    table = open(location[0].pathname).read()
    return render_to_response('table.html', {'table': table})

def output_graph(request):
    """
    Called with the /output/graph URL to fetch a graph.
    """
    location = ResultLocation.objects.filter(user_id=request.session.session_key, result_type='graph')
    filename = location[0].pathname
    return render_to_response('graph.html',
                              context_instance=RequestContext(request, {'filename': filename}))

@decorators.json_view
def upload(request):
    """
    Called from the /upload URL to upload some files.
    """
    if request.session.session_key == None:
        request.session.save()
    if request.method == 'POST':
        for filename in request.FILES.getlist('files'):
            piece = Piece()
            piece.user_id = request.session.session_key
            piece.save()
            piece.file = filename
            piece.save()
    uploaded = [os.path.basename(piece.file.name)
                for piece in Piece.objects.filter(user_id=request.session.session_key)]
    return uploaded, 200

@decorators.json_view
def delete(request):
    """
    Called from the /delete URL to remove a file from the list of files to import.
    """
    delete_these = request.GET.getlist('filenames[]')
    user_pieces = Piece.objects.filter(user_id=request.session.session_key)
    for piece in user_pieces:
        if os.path.basename(piece.file.name) in delete_these:
            piece.delete()
            piece.file.storage.delete(piece.file.path)
    uploaded = [os.path.basename(piece.file.name)
                for piece in Piece.objects.filter(user_id=request.session.session_key)]
    return uploaded, 200

class MainView(generic.TemplateView):
    """
    Shows the main GUI thing.
    """
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        """
        Gets context data.
        """
        context = super(MainView, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

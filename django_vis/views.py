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

import traceback
import os
import simplejson as json
from django.views import generic
from django.conf import settings
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from jsonview import decorators
import settings
from vis.workflow import WorkflowManager

from django_vis.models import Piece

@decorators.json_view
def import_files(request):
    filepaths = [piece.file.path for piece in Piece.objects.filter(user_id=request.session.session_key)]
    wf = WorkflowManager(filepaths)
    wf.load('pieces')
    request.session['wf'] = wf
    return [
        {"Filename": os.path.basename(wf.metadata(i, 'pathname')),
         "Title": wf.metadata(i, 'title'),
         "Part Names": wf.metadata(i, 'parts'),
         "Offset": None,
         "Part Combinations": None,
         "Repeat Identical": False}
        for i in xrange(len(wf))
    ], 200
    
@decorators.json_view
def run_experiment(request):
    wf = request.session['wf']
    # Set metadata and settings
    updated_pieces = json.loads(request.GET['updated_pieces'])
    interval_quality = True if request.GET['quality'] == 'display' else False
    simple_intervals = True if request.GET['octaves'] == 'simple' else False
    for (i, piece) in enumerate(updated_pieces):
        wf.metadata(i, 'title', piece['title'])
        wf.metadata(i, 'parts', piece['partNames'])
        wf.settings(i, 'offset interval', None if piece['offset']=='' else float(piece['offset']))
        wf.settings(i, 'voice combinations', piece['partCombinations'])
        wf.settings(i, 'filter repeats', piece['repeatIdentical'])
    wf.settings(None, 'interval quality', interval_quality)
    wf.settings(None, 'simple intervals', simple_intervals)
    # run experiment
    output = request.GET['output']
    if 'intervals' == request.GET['experiment']:
        experiment = 'intervals'
    elif 'interval n-grams' == request.GET['experiment']:
        experiment = 'interval n-grams'
    else:
        # default experiment; it's the one with less work... just to avoid a crash
        experiment = 'intervals'
    if 'lilypond' == output:
        # output('LilyPond') requires not counting frequency
        wf.settings(None, 'count frequency', False)
    n = None if request.GET['n'] == '' else int(request.GET['n'])
    topx = None if request.GET['topx'] == '' else int(request.GET['topx'])
    threshold = None if request.GET['threshold'] == '' else int(request.GET['threshold'])
    if request.GET['experiment'] == 'intervals':
        wf.run('intervals')
    else:
        wf.settings(0, 'n', n)
        wf.run('interval n-grams')
    # produce output
    filename = request.session.session_key
    if output == 'table':
        filename = filename + '.html'
        wf.export('HTML', "%s%s" % (settings.MEDIA_ROOT, filename), top_x=topx, threshold=threshold)
    elif output == 'graph':
        wf.output('R histogram', "%s%s" % (settings.MEDIA_ROOT, filename), top_x=topx, threshold=threshold)
        filename = filename + '.png'
    elif output == 'lilypond':
        wf.output('LilyPond', "%s%s" % (settings.MEDIA_ROOT, filename), top_x=topx, threshold=threshold)

        #fsock = open(settings.MEDIA_ROOT + filename + '.pdf', 'r')
        zell = {'mimetype': 'application/pdf',
                'Content-Disposition': 'attachment; filename=%s%s.pdf' % (settings.MEDIA_URL, filename),
                'score_location': '%s%s.pdf' % (settings.MEDIA_URL, filename),
                'type': 'lilypond'}
        return zell, 200
    else:
        pass
    return {'type': output}, 200
            
def output_table(request):
    filename = request.session.session_key + '.html'
    table = open("%s%s" % (settings.MEDIA_ROOT, filename)).read()
    return render_to_response('table.html', {'table': table})
    
def output_graph(request, filename=None):
    filename = request.session.session_key + '.png'
    return render_to_response('graph.html', context_instance=RequestContext(request, {'filename': filename}))
    
def output_score(request, filename=None):
    filename = request.session.session_key + '.pdf'
    return render_to_response('graph.html', context_instance=RequestContext(request, {'filename': filename}))

@decorators.json_view
def upload(request):
    # Handle file upload
    if request.session.session_key == None:
        request.session.save()
    if request.method == 'POST':
        for file in request.FILES.getlist('files'):
            piece = Piece()
            piece.user_id = request.session.session_key
            piece.save()
            piece.file = file
            piece.save()
    uploaded = [os.path.basename(piece.file.name) for piece in Piece.objects.filter(user_id=request.session.session_key)]
    return uploaded, 200
    
@decorators.json_view
def delete(request):
    delete_these = request.GET.getlist('filenames[]')
    user_pieces = Piece.objects.filter(user_id=request.session.session_key)
    for piece in user_pieces:
        if os.path.basename(piece.file.name) in delete_these:
            piece.delete()
            piece.file.storage.delete(piece.file.path)
    uploaded = [os.path.basename(piece.file.name) for piece in Piece.objects.filter(user_id=request.session.session_key)]
    return uploaded, 200
    
class MainView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

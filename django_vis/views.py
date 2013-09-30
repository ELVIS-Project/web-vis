#!/usr/bin/env python
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------------------------------
# Program Name:           django-vis
# Program Description:    Web-based User Interface for vis
#
# Filename:               django-vis/views.py
# Purpose:                ????
#
# Copyright (C) 2013 Jamie Klassen, Saining Li
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

import os
from django.views import generic
from jsonview import decorators
import settings
from vis.models import indexed_piece
from vis.analyzers import indexers


@decorators.json_view
def import_files(request):
    filepaths = [os.path.join(settings.TEST_CORPUS_PATH, fname)
                 for fname in request.GET.getlist('filenames[]')]
    indexed_pcs = [indexed_piece.IndexedPiece(fpath) for fpath in filepaths]
    for piece in indexed_pcs:
        piece.get_data([indexers.noterest.NoteRestIndexer])
    return [
        {"Path": ind_pc.metadata('pathname'),
         "Title": ind_pc.metadata('title'),
         "Part Names": ind_pc.metadata('parts'),
         "Offset": [0.5],
         "Part Combinations": '(none selected)',
         "Repeat Identical": False}
        for ind_pc in indexed_pcs
    ], 200
    
@decorators.json_view
def analyze(request):
    return 200


class MainView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['settings'] = settings
        return context

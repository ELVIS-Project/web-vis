/*
 * Program Name:           django-vis
 * Program Description:    Web-based User Interface for vis
 *
 * Filename:               ko-binding-handlers.js
 * Purpose:                ????
 *
 * Copyright (C) 2013 Jamie Klassen, Saining Li
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

ko.bindingHandlers.selectedRows = {
    init: function (element, valueAccessor, allBindings, viewModel) {
        // maybe should throw an error if the element is not a datatable
        $(element).parent().on("selectionChanged", function () {
            var value, selectedData, tools, models, selectedModels;
            tools = TableTools.fnGetInstance($(element).parent().attr('id'));
            selectedData = tools.fnGetSelectedData();
            models = viewModel.items();
            value = valueAccessor();
            selectedModels = new Array();
            for (var i = 0; i < selectedData.length; ++i) {
                for (var j = 0; j < models.length; ++j) {
                    if (_.isEqual(selectedData[i], ko.toJS(models[j]))) {
                        selectedModels.push(models[j]);
                    }
                }
            }
            value(selectedModels);
        });
    },
    update: function (element, valueAccessor, allBindingsAccessor, viewModel) {
        var parent, tools, val, data, dt;
        parent = $(element).parent();
        tools = TableTools.fnGetInstance(parent.attr("id"));
        val = ko.unwrap(valueAccessor());
        data = viewModel.items();
        dt = parent.dataTable();
        for (var i = 0; i < val.length; ++i) {
            for (var j = 0; j < data.length; ++j) {
                if (_.isEqual(ko.toJS(data[j]), val[i])) tools.fnSelect(dt.fnGetNodes(j));
            }
        }
    }
};
ko.bindingHandlers.tableData = {
    init: function (element, valueAccessor) {
        var data, value;
        data = $(element).dataTable().fnGetData();
        value = valueAccessor();
        for (var i = 0; i < data.length; ++i) {
            value.push(data[i]);
        }
    },
    update: function (element, valueAccessor) {
        var val = ko.unwrap(valueAccessor());
        var dt = $(element).dataTable();
        dt.fnClearTable();
        dt.fnAddData(val);
    }
};
var selectedItem = function (element) {
    return $(element).wizard('selectedItem').step;
};
ko.bindingHandlers.wizardStep = {
    init: function (element, valueAccessor) {
        $(element).on('changed', function () {
            var value = valueAccessor();
            value(selectedItem(element));
        });
    },
    update: function (element, valueAccessor) {
        var tryNext, value, val;
        tryNext = function (direction) {
            var curVal;
            curVal = selectedItem(element);
            if (direction) $(element).wizard('next');
            else $(element).wizard('previous');
            return curVal != selectedItem(element);
        };
        value = valueAccessor();
        val = ko.unwrap(value);
        while (val > selectedItem(element)) if (!tryNext(true)) break;
        while (val < selectedItem(element)) if (!tryNext(false)) break;
        value(selectedItem(element));
    }
};

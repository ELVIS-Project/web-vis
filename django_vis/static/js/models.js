/*
 * Program Name:           django-vis
 * Program Description:    Web-based User Interface for vis
 *
 * Filename:               ko-binding-models.js
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

function SelectableArray () {
    this.items = ko.observableArray();
    this.selectedItems = ko.observableArray();
}
SelectableArray.prototype.removeSelected = function () {
    var selected;
    selected = this.selectedItems();
    this.items.remove(function (item) {
        for (var i = 0; i < selected.length; ++i)
            if (_.isEqual(selected[i], item)) return true;
        return false;
    });
    this.selectedItems.removeAll();
    this.selectedItems.valueHasMutated();
    this.items.valueHasMutated();
};

function ListOfFiles () {
    SelectableArray.call(this);
    this.items = ko.observableArray([
        {"Filename": "bwv77.mxl"},
        {"Filename": "madrigal51.mxl"},
        {"Filename": "madrigal51.mxl"}
    ]);
}
ListOfFiles.prototype = Object.create(SelectableArray.prototype);
ListOfFiles.prototype.constructor = ListOfFiles;

function ListOfPieces () {
    SelectableArray.call(this);
    this.items = ko.observableArray();
}
ListOfPieces.prototype = Object.create(SelectableArray.prototype);
ListOfPieces.prototype.constructor = ListOfPieces;

function Wizard() {
    var self = this;
    self.state = ko.observable();
}

var Piece = function(filename, title, partNames, offset, partCombinations, repeatIdentical) {
    this.filename = ko.observable(filename);
    this.title = ko.observable(title);
    this.partNames = ko.observableArray(partNames);
    this.offset = ko.observable(offset);
    this.partCombinations = ko.observable(partCombinations);
    this.repeatIdentical = ko.observable(repeatIdentical);
}

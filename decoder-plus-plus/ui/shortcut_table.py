# vim: ts=8:sts=8:sw=8:noexpandtab
#
# This file is part of Decoder++
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5 import QtCore
from PyQt5.QtCore import QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTableView
from qtpy import QtWidgets

from ui.shortcut_table_item_delegate import ShortcutTableItemDelegate


class ShortcutTable(QTableView):

    shortcutUpdated = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')

    def __init__(self, parent, shortcuts):
        super(ShortcutTable, self).__init__(parent)
        self._init_model(shortcuts)
        self._init_headers()
        self._init_proxy_model()
        self._editing_started = False
        # BUG: Catching the tab-key in shortcut-table does not work correctly. Instead another column gets selected.
        # WORKAROUND: Disabling feature of assigning keyboard-shortcut by key-press as long as there is no permanent fix for this.
        # TODO: Catch tab-key in ShortcutTableItemDelegate (or in QTableView) when in edit-mode.
        # NOTES:
        # - installed event-filters in ShortcutTableItemDelegate and QTableView. Both didn't catch the tab-key ...
        # - checked the keyPressEvent / keyReleaseEvent / event in ShortcutTableItemDelegate and QTableView
        #       * only ShortcutTable got an TAB-key in the keyReleaseEvent but at this point the other cell was
        #         already selected and there was/is no easy way to know which cell was selected before.
        #self._init_item_delegate()

    def _init_item_delegate(self):
        self.setItemDelegate(ShortcutTableItemDelegate(self))

    def _init_headers(self):
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        self.verticalHeader().hide()

    def _init_model(self, shortcuts):
        model = QStandardItemModel(len(shortcuts), 3)
        model.setHorizontalHeaderLabels(["Id", "Name", "Shortcut"])
        for index, shortcut in enumerate(shortcuts):
            name_item = QStandardItem(shortcut.name())
            name_item.setFlags(name_item.flags() ^ QtCore.Qt.ItemIsEditable)
            model.setItem(index, 0, QStandardItem(shortcut.id()))
            model.setItem(index, 1, name_item)
            model.setItem(index, 2, QStandardItem(shortcut.key()))
        model.itemChanged.connect(self._shortcut_changed_event)
        self.setModel(model)
        self.setColumnHidden(0, True)

    def _init_proxy_model(self):
        filter_proxy_model = QSortFilterProxyModel()
        filter_proxy_model.setSourceModel(self.model())
        filter_proxy_model.setFilterKeyColumn(1)
        filter_proxy_model.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setModel(filter_proxy_model)

    def _shortcut_changed_event(self, item):
        # BUG: Cell changes to row below when editing cell is finished.
        # REQUIREMENT: The cell-selection should not change.
        # WORKAROUND: ???
        id = self.model().sourceModel().item(item.row(), 0).text()
        shortcut_key = self.model().sourceModel().item(item.row(), 2).text()
        self.shortcutUpdated.emit(id, shortcut_key)

    def setEditingStarted(self):
        self._editing_started = True

    def setEditingEnded(self):
        self._editing_started = False

    def hasEditingStarted(self):
        return self._editing_started

    def keyPressEvent(self, event):
        # BUG: Using Enter-Key to go into Edit-Mode results in an immediate closing of the selected cell.
        # WORKAROUND: The ItemDelegate is responsible for this behaviour. To fix this issue a custom editing-started
        #             variable is used to inform the ItemDelegate when the Enter-Key was being pressed.
        if event.key() == QtCore.Qt.Key_Return:
            self.edit(self.selectionModel().currentIndex())
            self.setEditingStarted()
            return
        super(__class__, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        self.setEditingEnded()
        super(__class__, self).keyReleaseEvent(event)

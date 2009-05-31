#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2008  Brian G. Matherly
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
"""
The "plug" package for handling plugins in Gramps.
"""

from _plugin import Plugin
from _manager import PluginManager
from _import import ImportPlugin
from _export import ExportPlugin
from _docgenplugin import DocGenPlugin
from utils import *

__all__ = [ "docbackend", "docgen", "menu", Plugin, PluginManager, 
            ImportPlugin, ExportPlugin, DocGenPlugin ]

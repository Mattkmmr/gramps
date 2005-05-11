#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2000-2005  Donald N. Allingham
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

# $Id$

#-------------------------------------------------------------------------
#
# Python modules
#
#-------------------------------------------------------------------------
from gettext import gettext as _

#-------------------------------------------------------------------------
#
# GTK/Gnome modules
#
#-------------------------------------------------------------------------
import gtk
import gtk.glade
import gnome

#-------------------------------------------------------------------------
#
# gramps modules
#
#-------------------------------------------------------------------------
import Sources
import Witness
import const
import Utils
import AutoComp
import RelLib
import Date
import DateHandler
import ImageSelect
import DateEdit
from QuestionDialog import WarningDialog, ErrorDialog

#-------------------------------------------------------------------------
#
# EventEditor class
#
#-------------------------------------------------------------------------
class EventEditor:

    def __init__(self,parent,name,elist,trans,event,def_placename,
                 read_only, cb, def_event=None, noedit=False):
        self.parent = parent
        self.db = self.parent.db
        if event:
            if self.parent.child_windows.has_key(event.get_handle()):
                self.parent.child_windows[event.get_handle()].present(None)
                return
            else:
                self.win_key = event.get_handle()
        else:
            self.win_key = self
        self.event = event
        self.child_windows = {}
        self.trans = trans
        self.callback = cb
        self.path = self.db.get_save_path()
        self.plist = []
        self.pmap = {}

        self.dp = DateHandler.parser
        self.dd = DateHandler.displayer

        values = {}
        for v in elist:
            values[v] = 1
        for vv in self.db.get_person_event_type_list():
            v = _(vv)
            values[v] = 1
            
        self.elist = values.keys()
        self.elist.sort()

        for key in self.parent.db.get_place_handles():
            title = self.parent.db.get_place_from_handle(key).get_title()
            self.pmap[title] = key

        if event:
            self.srcreflist = self.event.get_source_references()
            self.witnesslist = self.event.get_witness_list()
            if not self.witnesslist:
                self.witnesslist = []
            self.date = Date.Date(self.event.get_date_object())
            transname = const.display_event(event.get_name())
            # add the name to the list if it is not already there. This
            # tends to occur in translated languages with the 'Death'
            # event, which is a partial match to other events
            #if not transname in elist:
            #    elist.append(transname)
        else:
            self.srcreflist = []
            self.witnesslist = []
            self.date = Date.Date(None)

        self.top = gtk.glade.XML(const.dialogFile, "event_edit","gramps")

        self.window = self.top.get_widget("event_edit")
        title_label = self.top.get_widget('title')

        if name == ", ":
            etitle = _('Event Editor')
        else:
            etitle = _('Event Editor for %s') % name

        Utils.set_titles(self.window,title_label, etitle,
                         _('Event Editor'))
        
        self.place_field = self.top.get_widget("eventPlace")
        self.place_field.set_editable(not noedit)
        self.cause_field = self.top.get_widget("eventCause")
        self.cause_field.set_editable(not noedit)
        self.slist = self.top.get_widget("slist")
        self.wlist = self.top.get_widget("wlist")
        self.place_combo = self.top.get_widget("eventPlace_combo")
        self.date_field  = self.top.get_widget("eventDate")
        self.date_field.set_editable(not noedit)
        self.descr_field = self.top.get_widget("event_description")
        self.descr_field.set_editable(not noedit)
        self.note_field = self.top.get_widget("eventNote")
        self.note_field.set_editable(not noedit)
        self.event_menu = self.top.get_widget("personal_events")
        self.priv = self.top.get_widget("priv")
        self.priv.set_sensitive(not noedit)
        self.sources_label = self.top.get_widget("sources_tab")
        self.notes_label = self.top.get_widget("note_tab")
        self.general_label = self.top.get_widget("general_tab")
        self.gallery_label = self.top.get_widget("gallery_tab")
        self.witnesses_label = self.top.get_widget("witness_tab")
        self.flowed = self.top.get_widget("eventflowed")
        self.flowed.set_sensitive(not noedit)
        self.preform = self.top.get_widget("eventpreform")
        self.preform.set_sensitive(not noedit)
        self.ok = self.top.get_widget('ok')
        
        self.ok.set_sensitive(not noedit)
            
        if read_only or noedit:
            self.event_menu.set_sensitive(False)
            self.date_field.grab_focus()

        add_src = self.top.get_widget('add_src')
        add_src.set_sensitive(not noedit)
        del_src = self.top.get_widget('del_src')
        del_src.set_sensitive(not noedit)

        self.sourcetab = Sources.SourceTab(
            self.srcreflist, self, self.top, self.window, self.slist,
            add_src, self.top.get_widget('edit_src'), del_src,
            self.db.readonly)

        add_witness = self.top.get_widget('add_witness')
        add_witness.set_sensitive(not noedit)
        edit_witness = self.top.get_widget('edit_witness')
        del_witness = self.top.get_widget('del_witness')
        del_witness.set_sensitive(not noedit)
        
        self.witnesstab = Witness.WitnessTab(
            self.witnesslist, self, self.top, self.window, self.wlist,
            add_witness, edit_witness, del_witness)

        AutoComp.fill_combo(self.event_menu,self.elist)
        AutoComp.fill_entry(self.place_field,self.pmap.keys())

        if event != None:
            self.event_menu.child.set_text(transname)
            if (def_placename):
                self.place_field.set_text(def_placename)
            else:
                place_handle = event.get_place_handle()
                if not place_handle:
                    place_name = u""
                else:
                    place_name = self.db.get_place_from_handle(place_handle).get_title()
                self.place_field.set_text(place_name)

            self.date_field.set_text(self.dd.display(self.date))
            self.cause_field.set_text(event.get_cause())
            self.descr_field.set_text(event.get_description())
            self.priv.set_active(event.get_privacy())
            
            self.note_field.get_buffer().set_text(event.get_note())
            if event.get_note():
                self.note_field.get_buffer().set_text(event.get_note())
                Utils.bold_label(self.notes_label)
                if event.get_note_format() == 1:
                    self.preform.set_active(1)
                else:
                    self.flowed.set_active(1)
            if event.get_media_list():
                Utils.bold_label(self.gallery_label)
        else:
            if def_event:
                self.event_menu.child.set_text(def_event)
            if def_placename:
                self.place_field.set_text(def_placename)
        self.date_check = DateEdit.DateEdit(self.date,
                                        self.date_field,
                                        self.top.get_widget("date_stat"),
                                        self.window)
        if not event:
            event = RelLib.Event()
        self.icon_list = self.top.get_widget("iconlist")
        self.gallery = ImageSelect.Gallery(event, self.db.commit_event,
                                           self.path, self.icon_list,
                                           self.db,self,self.window)

        self.top.signal_autoconnect({
            "on_switch_page"            : self.on_switch_page,
            "on_help_event_clicked"     : self.on_help_clicked,
            "on_ok_event_clicked"       : self.on_event_edit_ok_clicked,
            "on_cancel_event_clicked"   : self.close,
            "on_event_edit_delete_event": self.on_delete_event,
            "on_addphoto_clicked"       : self.gallery.on_add_media_clicked,
            "on_selectphoto_clicked"    : self.gallery.on_select_media_clicked,
            "on_deletephoto_clicked"    : self.gallery.on_delete_media_clicked,
            "on_edit_properties_clicked": self.gallery.popup_change_description,
            "on_editphoto_clicked"      : self.gallery.on_edit_media_clicked,
            })

        self.top.get_widget('del_obj').set_sensitive(not noedit)
        self.top.get_widget('sel_obj').set_sensitive(not noedit)
        self.top.get_widget('add_obj').set_sensitive(not noedit)

        Utils.bold_label(self.general_label)

        try:
            self.window.set_transient_for(self.parent.window)
        except AttributeError:
            pass
        self.add_itself_to_menu()
        self.window.show()

    def on_delete_event(self,obj,b):
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_menu()

    def close(self,obj):
        self.gallery.close()
        self.close_child_windows()
        self.remove_itself_from_menu()
        self.window.destroy()

    def close_child_windows(self):
        for child_window in self.child_windows.values():
            child_window.close(None)
        self.child_windows = {}

    def add_itself_to_menu(self):
        self.parent.child_windows[self.win_key] = self
        if not self.event:
            label = _("New Event")
        else:
            label = self.event.get_name()
        if not label.strip():
            label = _("New Event")
        label = "%s: %s" % (_('Event'),label)
        self.parent_menu_item = gtk.MenuItem(label)
        self.parent_menu_item.set_submenu(gtk.Menu())
        self.parent_menu_item.show()
        self.parent.winsmenu.append(self.parent_menu_item)
        self.winsmenu = self.parent_menu_item.get_submenu()
        self.menu_item = gtk.MenuItem(_('Event Editor'))
        self.menu_item.connect("activate",self.present)
        self.menu_item.show()
        self.winsmenu.append(self.menu_item)

    def remove_itself_from_menu(self):
        if self.window:
            del self.parent.child_windows[self.win_key]
        self.menu_item.destroy()
        self.winsmenu.destroy()
        self.parent_menu_item.destroy()

    def present(self,obj):
        self.window.present()

    def on_help_clicked(self,obj):
        """Display the relevant portion of GRAMPS manual"""
        gnome.help_display('gramps-manual','adv-ev')

    def get_place(self,field):
        text = unicode(field.get_text().strip())
        if text:
            if self.pmap.has_key(text):
                return self.db.get_place_from_handle(self.pmap[text])
            else:
                place = RelLib.Place()
                place.set_title(text)
                trans = self.db.transaction_begin()
                self.db.add_place(place,trans)
                self.db.transaction_commit(trans,_("Add Place"))
                return place
        else:
            return None

    def on_event_edit_ok_clicked(self,obj):

        ename = unicode(self.event_menu.child.get_text())

        if not ename.strip():
            ErrorDialog(_("Event does not have a type"),
                        _("You must specify an event type "
                          "before you can save the event"))
            return

        #self.date = self.dp.parse(unicode(self.date_field.get_text()))
        ecause = unicode(self.cause_field.get_text())
        eplace_obj = self.get_place(self.place_field)
        buf = self.note_field.get_buffer()

        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        enote = unicode(buf.get_text(start,stop,False))
        eformat = self.preform.get_active()
        edesc = unicode(self.descr_field.get_text())
        epriv = self.priv.get_active()

        if ename not in self.elist:
            WarningDialog(
                _('New event type created'),
                _('The "%s" event type has been added to this database.\n'
                  'It will now appear in the event menus for this database') % ename)
            self.elist.append(ename)
            self.elist.sort()

        just_added = False
        if self.event == None:
            self.event = RelLib.Event()
            self.event.set_handle(Utils.create_id())
            self.event.set_source_reference_list(self.srcreflist)
            self.event.set_witness_list(self.witnesslist)
            just_added = True
        
        self.update_event(ename,self.date,eplace_obj,edesc,enote,eformat,
                          epriv,ecause)
        
        self.close(obj)
        if self.callback:
            self.callback(self.event)

    def update_event(self,name,date,place,desc,note,format,priv,cause):
        if place:
            if self.event.get_place_handle() != place.get_handle():
                self.event.set_place_handle(place.get_handle())
                self.parent.lists_changed = 1
        else:
            if self.event.get_place_handle():
                self.event.set_place_handle("")
                self.parent.lists_changed = 1
        
        if self.event.get_name() not in [self.trans.find_key(name)]:
            self.event.set_name(self.trans.find_key(name))
            self.parent.lists_changed = 1
        
        if self.event.get_description() != desc:
            self.event.set_description(desc)
            self.parent.lists_changed = 1

        if self.event.get_note() != note:
            self.event.set_note(note)
            self.parent.lists_changed = 1

        if self.event.get_note_format() != format:
            self.event.set_note_format(format)
            self.parent.lists_changed = 1

        dobj = self.event.get_date_object()

        self.event.set_source_reference_list(self.srcreflist)
        self.event.set_witness_list(self.witnesslist)
        
        if not dobj.is_equal(date):
            self.event.set_date_object(date)
            self.parent.lists_changed = 1

        if self.event.get_cause() != cause:
            self.event.set_cause(cause)
            self.parent.lists_changed = 1

        if self.event.get_privacy() != priv:
            self.event.set_privacy(priv)
            self.parent.lists_changed = 1

    def on_switch_page(self,obj,a,page):
        buf = self.note_field.get_buffer()
        start = buf.get_start_iter()
        stop = buf.get_end_iter()
        text = unicode(buf.get_text(start,stop,False))
        if text:
            Utils.bold_label(self.notes_label)
        else:
            Utils.unbold_label(self.notes_label)

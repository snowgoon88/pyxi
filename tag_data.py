# image_data.py
# -*- coding: utf-8 -*-
"""
Store information about tags
"""
__docformat__ = "restructuredtext en"

import gtk
import xml.etree.ElementTree as ET

# **********************************************************************************
# ********************************************************************** TagDataTree
# **********************************************************************************
class TagDataTree(object):
    """
    Store information about the tags in a tree:
    - name : string
    - selected : boolean
    - editable : boolean

    A tag cannot be duplicated.

    Through 'self.to_save', the tags are monitored for change since last load or write.

    'self.tag_set' is a dictionary {tag : .X.Y.tag}
    'self.tag_element' is an ElementTree version of the tags (XML struct)
    """
    # sec --------------------------------------------------------------------- init
    def __init__(self, filename = None):
        """
        Create void data structure and populate it.
        """
        # Build up the data structure as a gtk.TreeStore with 3 column
        self.tag_treestore = gtk.TreeStore(str, 'gboolean', 'gboolean')
        # self.build_default()
        # Create an 'ElementTree' version.
        self.tag_element = None
        # Create the set of tags (for ensuring unicity of tags)
        self.tag_set = {}
        # To monitor changes
        self.to_save = False

        if filename != None:
            self.load( filename )
        
    def build_default(self):
        """
        Populate self.tag_treestore with default values. Only for test.
        """
        gens_node = self.tag_treestore.append(None, ("Gens", False, False))
        self.tag_treestore.append(gens_node, ("Bob", False, False))
        self.tag_treestore.append(gens_node, ("Marcel", False, False))
        self.tag_treestore.append(gens_node, ("Louise", False, False))
        nature_node = self.tag_treestore.append(None, ("Nature", False, False))
        self.tag_treestore.append(nature_node, ("Foret", False, False))
        self.tag_treestore.append(nature_node, ("Lac", False, False))
        self.tag_treestore.append(nature_node, ("Montagne", False, False))

        self.to_save = True
    def build_example(self):
        """
        Populate with default values, using inner add functions.
        """
        try:
            gens_node = self.add_check_unique(None, "Gens")
            self.add_check_unique(gens_node, "Bob")
            self.add_check_unique(gens_node, "Marcel")
            self.add_check_unique(gens_node, "Louise")
            nature_node = self.add_check_unique(None, "Nature")
            self.add_check_unique(nature_node, "Foret")
            self.add_check_unique(nature_node, "Lac")
            self.add_check_unique(nature_node, "Montagne")
        except TagData_UnicityWarning as e:
            print "@@@",e.__class__.__name__, e
            print self.dump_str()

    # sec ---------------------------------------------------------------------- I/O
    def write(self, db_file_name):
        """
        Ecrit dans un fichier au format XML.
        """
        self.to_element()
        tree = ET.ElementTree( self.tag_element )
        tree.write(db_file_name)

        self.to_save = False
    
    def load(self, db_file_name):
        """
        Lit dans un fichier au format XML.
        """
        tree = ET.parse( db_file_name)
        self.element_to_tagnode( tree.getroot(), None)
    
        self.to_save = False

    # sec ---------------------------------------------------------------------- str
    def __str__(self):
        return self.str_treestore(self.tag_treestore.iter_children(None), "", 0)
    def display_str(self):
        return self.str_treestore(self.tag_treestore.iter_children(None), "", 0)
    def dump_str(self):
        dump_str = self.str_treestore(self.tag_treestore.iter_children(None), "", 0,1,2)
        dump_str += "\n" + str(self.tag_set)
        dump_str += "\nTo be saved : " + str(self.to_save)
        return dump_str
#     def affiche(self):
#         """
#         Print the entire treestore.
#         """
#         print self.str_treestore(self.tag_treestore.iter_children(None), "", 0, 1)

    def str_treestore(self, iter, indent="", *args ): 
        """
        Print an element of self.tag_treestore and all its sub-nodes.
        """
        ret_str = ""
        while iter:
            ret_str = ret_str + indent + str(self.tag_treestore.get(iter, *args )) + "\n"
            ret_str += self.str_treestore(self.tag_treestore.iter_children(iter),
                                   indent+"  ", *args)
            iter = self.tag_treestore.iter_next(iter)
        return ret_str

    # sec -------------------------------------------------------- add/remove/update
    def add_check_unique(self, iter, tag):
        """
        Add 'tag' to 'tag_set' and the treestore if not existing.
        
        :Params:
        - path : where to add the tag in the TagTree
        - tag : tag to be added

        :Returns:
        - iter to the added tag

        :Throws:
        - TagData_UnicityWarning( 'tag: '+tag+' already in TagDataTree')
        """
        # if exists -> raise Exception
        if( tag in self.tag_set.keys()):
            raise TagData_UnicityWarning( 'tag: '+tag+' already in TagDataTree')

        #iter = None
        #if( path is not None ):
        #    iter = self.tag_treestore.get_iter( path )
        iter_added =  self.tag_treestore.append(iter, ( tag, False, True))
        path_added = self.tag_treestore.get_path(iter_added) 
        # add it to the tagtree
        self.tag_set[tag] = self.strpath_from_path(path_added)
        self.to_save = True
        return iter_added

    def update_check_unique(self, iter, new_tag):
        """
        Update 'tag_set' and the treestore with the 'new_tag' if not existing.
        
        :Params:
        - iter : where to add the tag in the TagTree
        - new_tag : new value for tag

        :Throws:
        - TagData_UnicityWarning( 'tag: '+tag+' already in TagDataTree')
        """
        
        tmp_changed = self.to_save # will be modified by remove
        old_tag = self.tag_treestore.get_value(iter, 0)
        #self.tag_set.remove( old_tag )
        old_strpath = self.tag_set.pop( old_tag )
        
        # if exists -> raise Exception
        if( new_tag in self.tag_set.keys()):
            self.tag_set[old_tag] = old_strpath
            # back to old setting
            self.to_save = tmp_changed
            raise TagData_UnicityWarning( 'tag: '+new_tag+' already in TagDataTree')

        self.tag_treestore.set_value(iter, 0, new_tag)
        strpath = self.strpath_from_path( self.tag_treestore.get_path(iter) )
        self.tag_set[new_tag] = strpath
        self.to_save = True

    def remove(self, iter):
        """
        Remove the tag from 'tag_set' and the treestore.
        
        :Params:
        - iter : where to remove the tag in the TagTree
        """
        self.tag_set.pop( self.tag_treestore.get_value( iter, 0))
        self.tag_treestore.remove(iter)
        self.to_save = True

    def is_in(self, tag):
        """
        :Return:
        - True if tag is already in the set of tags
        """
        return (tag in self.tag_set)

    # sec ---------------------------------------------------------------- selection
    def get_selected_tag(self):
        """
        Return the list of selected tags
        """
        return self.rec_selected_tag(self.tag_treestore.iter_children(None), [])
    def rec_selected_tag(self,iter,selected):
        """
        For a given 'iter' of treestore nodes, populate list of 'selected' and
        call same function on subnodes.
        """
        while iter:
            if self.tag_treestore.get_value( iter, 1) == True:
                selected.append(self.tag_treestore.get_value( iter, 0))
            selected = self.rec_selected_tag( self.tag_treestore.iter_children(iter),
                                              selected)
            iter = self.tag_treestore.iter_next(iter)
        return selected

    def get_selected_tag_strpath(self):
        """
        Return the list of selected tags as strpath
        """
        return self.rec_selected_tag_strpath(self.tag_treestore.iter_children(None), [])
    def rec_selected_tag_strpath(self,iter,selected):
        """
        For a given 'iter' of treestore nodes, populate list of 'selected' and
        call same function on subnodes.
        """
        while iter:
            if self.tag_treestore.get_value( iter, 1) == True:
                selected.append( 
                    self.strpath_from_path( self.tag_treestore.get_path( iter ) ))
            selected = self.rec_selected_tag_strpath( self.tag_treestore.iter_children(iter),
                                              selected)
            iter = self.tag_treestore.iter_next(iter)
        return selected

    def clean_selected(self):
        """
        Unselect all tags in treestore.
        """
        self.rec_clean_selected(self.tag_treestore.iter_children(None))
    def rec_clean_selected(self,iter):
        """
        For a given 'iter' of treestore nodes, unselect them and call
        same function on subnodes
        """
        while iter:
            self.tag_treestore.set_value(iter, 1, False)
            self.rec_clean_selected( self.tag_treestore.iter_children(iter))
            iter = self.tag_treestore.iter_next(iter)

    # sec -------------------------------------------------------- strpath_from_path
    def strpath_from_path(self, path):
        """
        From a path of treestore, build a str .X.Y.Tags.
        
        :Return:
        A str full path (.X.Y.Tags) of the tags at path.
        """
        strpath = ''
        for long in range(1,len(path)+1):
            strpath = strpath + '.' + self.tag_treestore[path[0:long]][0]
        return strpath

    # sec -------------------------------------------------------- ElementTree (XML)
    def to_element(self):
        """
        Turn the treestore to a structure of ET.Element stored in self.tag_element
        """
        self.tag_element = ET.Element("root")
        self.tagnode_to_element( self.tag_treestore.iter_children(None),
                                 self.tag_element )

    def tagnode_to_element(self, tag_iter, et_node):
        """
        Create a node ET.Element for the current node and recursively iterate
        to all subnode.
        Element node is a 'tag' with str val.

        :Param:
        - tag_iter: iterable through treestore nodes of same level
        - et_node: current ET.Element to which one ET.Element by node will be added 
        """
        while tag_iter:
            new_node = ET.SubElement(et_node,"tag")
            new_node.text = self.tag_treestore.get_value(tag_iter, 0 )
            self.tagnode_to_element( self.tag_treestore.iter_children(tag_iter),
                                     new_node )
            tag_iter = self.tag_treestore.iter_next(tag_iter)
        return None

    def element_to_tagnode(self, et_node, tag_iter):
        """
        Add nodes from et_node to the treestore, by default not editable
        and not selected.
        
        :Param:
        - et_node: iterable of ET.Element
        - tag_iter : where are the new nodes and subnodes added in treestore

        :Throws:
        - TagData_UnicityWarning( 'tag:' + node.text + ' already in TagData')
        """
        for node in et_node:
            print "tag_iter=",tag_iter
            tmp_tagiter = self.add_check_unique( tag_iter, node.text )
            #if( node.text not in self.tag_set):
            #    self.tag_set.add( node.text )
            #    tmp_tagiter = self.tag_treestore.append(tag_iter, 
            #                                            (node.text, False, False))
            #    print "added ", self.strpath_from_path( self.tag_treestore.get_path( tmp_tagiter))
            #else:
            #    raise TagData_UnicityWarning( 'tag:' + node.text + ' already in TagData')
            self.element_to_tagnode( node, tmp_tagiter )
# **********************************************************************************

# **********************************************************************************
# ********************************************************************** TagDataTree
# **********************************************************************************
class TagDataSearch(object):
    """
    @todo Tester.
    """
    # sec -------------------------------------------------------------------- init
    def __init__(self, tag_pattern_list, tag_data=None):
        self.tag_data = tag_data
        self.tag_searched = {}
        self.tag_pattern_list = tag_pattern_list
        #
        # concatenation des pattern
        #self.pattern = ''
        #for t in tag_pattern_list:
        #    self.pattern += t 
        #print self.pattern

    def is_in(self, keyword):
        print "looking for ",keyword
        # first, may already be in tag_searched
        try:
            #print self.tag_searched[keyword]," Seen"
            return self.tag_searched[keyword]
        # ok, so now we have to look for it
        except KeyError:
            try:
                strpath = self.tag_data.tag_set[keyword]
                print "strpath ",strpath
                for pattern in self.tag_pattern_list:
                    if strpath.find( pattern ) != -1:
                        self.tag_searched[keyword] = True
                        print "OK ", keyword
                        return True
            except KeyError:
                self.tag_searched[keyword] = False
                print "Not found ", keyword
                #return False
        self.tag_searched[keyword] = False
        print "No ", keyword
        return False
    def is_in_all(self, keyword):
        print "looking for ",keyword
        # first, may already be in tag_searched
        try:
            #print self.tag_searched[keyword]," Seen"
            return self.tag_searched[keyword]
        # ok, so now we have to look for it
        except KeyError:
            try:
                strpath = self.tag_data.tag_set[keyword]
                print "strpath ",strpath
                for pattern in self.tag_pattern_list:
                    if strpath.find( pattern ) == -1:
                        print "No ", keyword
                        self.tag_searched[keyword] = False
                        return False
                self.tag_searched[keyword] = True
                print "OK ", keyword
                return True
            except KeyError:
                self.tag_searched[keyword] = False
                print "Not found ", keyword
                #return False
        self.tag_searched[keyword] = False
        print "No ", keyword
        return False
    def one_is_in(self, keyword_list):
        for k in keyword_list:
            if self.is_in( k ):
                return True
        return False
    def one_is_in_all(self, keyword_list):
        for k in keyword_list:
            if self.is_in_all( k ):
                return True
        return False

# **********************************************************************************
# ****************************************************************** TagData_Warning
# **********************************************************************************
class TagData_UnicityWarning(UserWarning):
    """
    Raised when trying to insert an existing tag to the TagData.
    """
    pass
# **********************************************************************************

# **********************************************************************************
# ******************************************************************** TagDataGadget
# **********************************************************************************
class TagDataGadget(gtk.Frame):
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    

    # ------------------------------------------------------------------------------
    # --------------------------------------------------------------------- __init__
    def __init__(self, tag_data=None):
        """
        :Param:
        - tag_data: a TagDataTree
        """
        gtk.Frame.__init__(self)
        # store tag_data
        self.tag_store = tag_data
        
        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.tag_store.tag_treestore)
        # allow the selection of more than one row
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        # listen for some events
        self.treeview.add_events(gtk.gdk.KEY_PRESS_MASK)
        self.treeview.connect("key-press-event", self.__on_key_press_event)

        # create the TreeViewColumn to display the tags
        self.tvcolumn0 = gtk.TreeViewColumn('Mot clef')
        # create a CellRendererText to render the tags
        self.text_cell = gtk.CellRendererText()
        #self.text_cell.set_property('editable', True)
        self.text_cell.connect('edited', self.__on_cell_edited, self.tag_store.tag_treestore)

        # add the cell to the tvcolumn and allow it to expand
        self.tvcolumn0.pack_start(self.text_cell, True)
        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        # and its editable capacity from column 2
        self.tvcolumn0.add_attribute(self.text_cell, 'text', 0)
        self.tvcolumn0.add_attribute(self.text_cell, 'editable', 2)
        # The toggle cellrenderer is setup and we allow it to be
        # changed (toggled) by the user.
        self.toggle_cell = gtk.CellRendererToggle()
        self.toggle_cell.set_property('activatable', True)
        self.toggle_cell.connect( 'toggled', self.__on_cell_toggled,
                                  (self.tag_store.tag_treestore, 1))
        # The columns active state is attached to the second column
        # in the model.  So when the model says True then the button
        # will show as active e.g on.
        self.tvcolumn1 = gtk.TreeViewColumn("Selection", self.toggle_cell )
        self.tvcolumn1.add_attribute( self.toggle_cell, "active", 1)

        # add columns
        self.treeview.append_column( self.tvcolumn0 )
        self.treeview.append_column( self.tvcolumn1 ) 

        self.treeview.show()

        # put it all into a scrolled window
        self.scroll_window = gtk.ScrolledWindow(hadjustment=None, vadjustment=None)
        # with always a vertical scrollbar
        self.scroll_window.set_policy(hscrollbar_policy=gtk.POLICY_AUTOMATIC,
                                      vscrollbar_policy=gtk.POLICY_ALWAYS)
        self.scroll_window.add_with_viewport( self.treeview )
        self.scroll_window.show()
        self.add( self.scroll_window )

    # ------------------------------------------------------------------------------
    # ----------------------------------------------------------__on_key_press_event
    def __on_key_press_event(self, widget, event):
        """
        """
        # keyval is in gtk.keysyms.Insert (par exemple)
        #print "TagDataGadget __on_key_press_event"
        #print "event.keyval =",event.keyval
        #print "event.string =",event.string
        #print "event.state =", event.state, event.state.__class__
        #print "event.group =",event.group
        #print event
        # Insert or Ctrl-i -> insert new tag
        if( event.keyval == gtk.keysyms.Insert or 
            ((event.keyval == gtk.keysyms.i or event.keyval == gtk.keysyms.I)
             and (event.state == gtk.gdk.CONTROL_MASK))):
             #and (event.state & gtk.gdk.CONTROL_MASK == True))):             
            self.insert_tag()
            return True  # NO event propagation
        # Delete or Ctrl-x -> delete_tag
        elif( event.keyval == gtk.keysyms.Delete or
            ((event.keyval == gtk.keysyms.x or event.keyval == gtk.keysyms.X)
             and (event.state == gtk.gdk.CONTROL_MASK))):
            self.delete_tag()
            return True  # NO event propagation
        # Ctrl-e -> edit tag
        elif( (event.keyval == gtk.keysyms.e or event.keyval == gtk.keysyms.E)
             and (event.state == gtk.gdk.CONTROL_MASK)):
            self.edit_tag()
            return True  # NO event propagation
        # Ctrl-p -> print_tree
        elif( (event.keyval == gtk.keysyms.p or  event.keyval == gtk.keysyms.P)
             and (event.state == gtk.gdk.CONTROL_MASK)):
            self.tag_store.affiche()
            return True  # NO event propagation
        # Ctrl-l -> print selection
        elif( (event.keyval == gtk.keysyms.l or event.keyval == gtk.keysyms.L)
             and (event.state == gtk.gdk.CONTROL_MASK)):
            print self.tag_store.get_selected_tag()
            return True  # NO event propagation
        # Ctrl-z -> clear selection
        elif( (event.keyval == gtk.keysyms.z or event.keyval == gtk.keysyms.Z)
             and (event.state == gtk.gdk.CONTROL_MASK)):
            print self.tag_store.clean_selected()
            return True  # NO event propagation
        # Ctrl-f -> print str_path
        elif( (event.keyval == gtk.keysyms.f or event.keyval == gtk.keysyms.F)
             and (event.state == gtk.gdk.CONTROL_MASK)):
            print self.print_strpath()
            return True  # NO event propagation
        # Ctrl-b -> print tag_set
        elif( (event.keyval == gtk.keysyms.b or event.keyval == gtk.keysyms.B)
             and (event.state == gtk.gdk.CONTROL_MASK)):
            print self.print_tag_set()
            return True  # NO event propagation
        
        return False #event propagation
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------- __on_cell_edited
    def __on_cell_edited(self, cell, path, new_text, user_data):
        """
        Called when a cell has been edited. Set its status to non-editable.

        :Param:
        - cell: (not used) cell edited
        - path: path to the treestore node edited
        - new_text: new value of the node
        - user_data: (not used)

        """
        iter = self.tag_store.tag_treestore.get_iter(path)
        # print "Cell edited : ",new_text
        # set cell new value if valid value
        try:
            self.tag_store.update_check_unique( iter, new_text )
        except TagData_UnicityWarning as warn:
            dialog = gtk.Dialog('Doublon in Tags', self.get_toplevel(),
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                ("Ok", gtk.RESPONSE_OK))
            dialog.vbox.pack_start(gtk.Label( warn.__str__() ))
            dialog.show_all()
            result = dialog.run()
            dialog.destroy()

        # and cannot be edited any more
        self.tag_store.tag_treestore.set_value(iter, 2, False)
        return False #allow event propagation

    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------ __on_cell_toggled
    def __on_cell_toggled(self, cell, path, user_data):
        """
        Called when a cell status has been changed.
        
        DRAFT: intelligent way to access data for changing state of button.

        :Param:
        - cell: (not used) cell edited
        - path: path to the treestore node edited
        - user_data: model,column
        """
        model, column = user_data
        model[path][column] = not model[path][column]
        return False #allow event propagation

    # ------------------------------------------------------------------------------
    # ---------------------------------------------------------------------      ???
    def __on_button_press_event(self, treeview, event):
        """
        Not used ???
        """
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor( path, col, 0)
                self.popup.popup( None, None, None, event.button, time)
                return 1
    
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------- insert_tag
    def insert_tag(self):
        """
        DRAFT: test how to retrieve selection list from treeview
        and insert new elements to tree that can be edited.

        If no row selected, a tag '_New_' is added to the root of the tree.
        If one row is selected, a tag '_New_' is added and can be edited.
        If more than one row is selected, nothing happens.
        """
        # print "** insert_tag**"
        (model, pathlist) = self.treeview.get_selection().get_selected_rows()
        if( len(pathlist) == 0):
            # print "Adding to Root"
            try:
                path_added = self.tag_store.add_check_unique( None, "_New_" )
                self.treeview.set_cursor(path_added, self.tvcolumn0, start_editing=True)
            except TagData_UnicityWarning as warn:
                dialog = gtk.Dialog('Doublon in Tags', self.get_toplevel(),
                                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                    ("Ok", gtk.RESPONSE_OK))
                dialog.vbox.pack_start(gtk.Label(warn.__str__()))
                dialog.show_all()
                result = dialog.run()
                dialog.destroy()
        elif( len(pathlist) == 1):
            # print "Insert possible"
            try:
                iter_added = self.tag_store.add_check_unique( self.tag_store.tag_treestore.get_iter(pathlist[0]), "_New_" )
                self.treeview.expand_row(pathlist[0], False)
                self.treeview.set_cursor(self.tag_store.tag_treestore.get_path(iter_added), self.tvcolumn0, start_editing=True)
            except TagData_UnicityWarning as warn:
                dialog = gtk.Dialog('Doublon in Tags', self.get_toplevel(),
                                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                    ("Ok", gtk.RESPONSE_OK))
                dialog.vbox.pack_start(gtk.Label(warn.__str__()))
                dialog.show_all()
                result = dialog.run()
                dialog.destroy()
        else:
            # print "More than one selection"
            pass

    # ------------------------------------------------------------------------------
    # --------------------------------------------------------------------- edit_tag
    def edit_tag(self):
        """
        DRAFT: edit a tag if only one row is selected
        """
        # print "** edit_tag**"
        (model, pathlist) = self.treeview.get_selection().get_selected_rows()
        if( len(pathlist) == 1):
            # print "Editing possible"
            iter = self.tag_store.tag_treestore.get_iter(pathlist[0])
            path = self.tag_store.tag_treestore.get_path(iter)
            # set editable
            self.tag_store.tag_treestore.set_value(iter,2,True)
            self.treeview.set_cursor(path, self.tvcolumn0, start_editing=True)
        else:
            # print "Not one selection"
            pass

    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------- delete_tag
    def delete_tag(self):
        """
        DRAFT: ask before deleting all tags selected.
        """
        # print "** delete_tag**"
        (model, pathlist) = self.treeview.get_selection().get_selected_rows()
        if( len(pathlist) >= 1 ):
            #ask confirmation by dialog
            dialog = gtk.Dialog('Suppress Tags ?', self.get_toplevel(),
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                                ("Ok", gtk.RESPONSE_OK, "Cancel", gtk.RESPONSE_CANCEL))
            dialog.vbox.pack_start(gtk.Label('On supprime VRAIMENT tout Ã§a ?'))
            dialog.show_all()
            result = dialog.run()
            if result == gtk.RESPONSE_OK:
                iter_list = []
                for path in pathlist:
                    iter_list.append(self.tag_store.tag_treestore.get_iter(path))
                for iter in iter_list:
                    self.tag_store.remove( iter )
            dialog.destroy()
    # ------------------------------------------------------------------------------
    # ---------------------------------------------------------------- print_strpath
    def print_strpath(self):
        """
        DRAFT : print full strPath of selected nodes
        """
        (model, pathlist) = self.treeview.get_selection().get_selected_rows()
        if( len(pathlist) >= 1 ):
            for path in pathlist:
                print self.tag_store.strpath_from_path( path )
    # ------------------------------------------------------------------------------
    # ------------------------------------------------------------------- to_element
    def print_tag_set(self):
        """
        DEBUG: print the set of 'unique' tags
        """
        print self.tag_store.tag_set
# **********************************************************************************

# **********************************************************************************
# ************************************************************************** TagData
# **********************************************************************************
class TagData(object):
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
    

    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title("Basic TreeView Example")

        self.window.set_size_request(200, 200)
        self.window.connect("delete_event", self.delete_event)
        # create a TreeStore with string and boolean
        #self.tag_store = gtk.TreeStore(str, 'gboolean')
        tag_store = TagDataTree("page.xhtml")

        self.tag_gadget = TagDataGadget( tag_store )
        self.tag_gadget.show()
        self.window.add(self.tag_gadget)
        self.window.show_all()
# **********************************************************************************

# **********************************************************************************
# ************************************************************************* TagGLADE
# **********************************************************************************
class TagGLADE(object):
    """
    """

    # sec --------------------------------------------------------------------- init
    def __init__(self ):
        """
        Read XML UI file and create.
        """
        builder = gtk.Builder()
        builder.add_from_file( "tag_data.glade" )

        self.tag_data_frame = builder.get_object( "tag_data_frame" )
        self.tag_data_treeview = builder.get_object( "tag_data_treeview" )
# **********************************************************************************
            


# sec ******************************************************************************
def main():
    gtk.main()

def test_basic():
    print "*** test_basic()"
    data = TagDataTree()
    data.build_example()
    data.write( "tmp/tag_data.xml" )
    print data.dump_str()
def test_load():
    print "*** test_load()"
    data = TagDataTree( "tmp/tag_data.xml" )
    print data.dump_str()

def test_gtk():
    tvexample = TagData()
    try:
        main()
    except TagData_UnicityWarning:
        #ask confirmation by dialog
        dialog = gtk.Dialog('Doublon in Tags', tvexample.window.get_toplevel(),
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            ("Ok", gtk.RESPONSE_OK))
        #dialog.vbox.pack_start(gtk.Label('On supprime VRAIMENT tout Ã§a ?'))
        dialog.show_all()
        result = dialog.run()
        dialog.destroy()


def test_glade():
    def cb_destroy(widget, data=None):
        """
        Destroy main window, ie: self
        """
        gtk.main_quit();
    
    # get data
    tag_data = TagDataTree()
    tag_data.build_example()

    # Need a high level window
    main_window = gtk.Window()
    # Connect destroy event
    main_window.connect( 'destroy', cb_destroy )
    
    # Get UI from glade
    tag_data_glade = TagGLADE()
    # connect to our treestore
    tag_data_glade.tag_data_treeview.set_model( tag_data.tag_treestore )
    main_window.add( tag_data_glade.tag_data_frame )
    
    main_window.show_all()
    gtk.main()

    
# sec ************************************************************************* MAIN
if __name__ == "__main__":
    #test_basic()
    #test_load()
    test_glade()

    #data = TagDataTree()
    #data.affiche()
    #data.to_element()
    #print data.tag_element.__repr__()
    # wrap it in an ElementTree instance, and save as XML
    #tree = ET.ElementTree(data.tag_element)
    #tree.write("page.xhtml")
    #data = TagDataTree("page.xhtml")
    #data.affiche()

# sec ************************************************************************** END
# Local Variables:
# coding:utf-8
# End:






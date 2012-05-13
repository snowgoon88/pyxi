#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Generic application to test a widget.
"""

import gtk

# **********************************************************************************
# ******************************************************************** TestComponent
# **********************************************************************************
class TestComponent(object):
    """
    The application has a menubar with 
    -test_menu : switch between toolbar style
    -component_menu : automatically build from component 'list_actions'
    a toolbar automatically build from component 'list_actions'
    and a component.
    """
    # sec --------------------------------------------------------------------- init
    def __init__(self, component):
        """
        """
        self._component = component
        self.build_gui()

        self.window.show()
    def build_gui(self):
        """
        Automatically build MenuBar, ToolBar and Component.
        """
        # Top level window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', lambda w: gtk.main_quit())
        self.window.set_title( 'Test Component' )
        
        # vbox for menu, toolbar and component
        vbox = gtk.VBox()
        vbox.show()
        self.window.add(vbox)
        # menu
        menubar = gtk.MenuBar()
        menubar.show()
        vbox.pack_start(menubar, expand=False)
        # menu for test
        test_menu = gtk.Menu()
        test_menu.show()
        icon_item = gtk.RadioMenuItem( group=None, label='Icons' )
        icon_item.connect( 'toggled',  self.__cb_switch_toolbar, gtk.TOOLBAR_ICONS )
        icon_item.show()
        test_menu.append( icon_item )
        label_item = gtk.RadioMenuItem( group=icon_item, label='Labels' )
        label_item.connect( 'toggled',  self.__cb_switch_toolbar, gtk.TOOLBAR_TEXT )
        label_item.show()
        test_menu.append( label_item )
        both_item = gtk.RadioMenuItem( group=icon_item, label='Icons+Labels' )
        both_item.activate()
        both_item.connect( 'toggled',  self.__cb_switch_toolbar, gtk.TOOLBAR_BOTH)
        both_item.show()
        test_menu.append( both_item )
        test_item = gtk.MenuItem("Test")
        test_item.show()
        test_item.set_submenu(test_menu)
        menubar.append(test_item)
        # menu for component
        component_menu = gtk.Menu()
        for action in self._component.list_actions:
            menu_item = action.create_menu_item()
            component_menu.append( menu_item)
        component_item = gtk.MenuItem("Component")
        component_item.show()
        component_item.set_submenu(component_menu)
        menubar.append(component_item)
        # toolbar
        self.toolbar = gtk.Toolbar()
        self.toolbar.show()
        self.toolbar.set_style(gtk.TOOLBAR_BOTH)  
        vbox.pack_start(self.toolbar, expand=False)
        for action in self._component.list_actions:
            toolitem = action.create_tool_item()
            self.toolbar.insert(toolitem, -1) #at the end
        # component
        self._component.show()
        vbox.pack_start( self._component, expand=True )
    # sec ----------------------------------------------------------------- callback
    def __cb_switch_toolbar(self, radiomenuitem, style, *args):
        if radiomenuitem.get_active():
            self.toolbar.set_style( style )
    # sec ---------------------------------------------------------------------- run
    def run(self):
        gtk.main()
# sec ******************************************************************************
def test_tagdata():
    import tag_data
    data = tag_data.TagDataTree()
    comp = tag_data.TagDataGadget( data )
    app = TestComponent( comp )
    app.run()
# sec ******************************************************************************
if __name__ == '__main__':
    test_tagdata()
# **********************************************************************************

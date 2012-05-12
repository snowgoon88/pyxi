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
    """
    
    def __init__(self, component):
        """
        """
        self._component = component
        self.build_gui()

        self.window.show()

    def run(self):
        gtk.main()

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
        for action in self._component.list_actions:
            menu_item = action.create_menu_item()
            menubar.append( menu_item)
        # toolbar
        toolbar = gtk.Toolbar()
        toolbar.show()
        vbox.pack_start(toolbar, expand=False)
        for action in self._component.list_actions:
            toolitem = action.create_tool_item()
            toolbar.insert(toolitem, -1) #at the end
        # component
        self._component.show()
        vbox.pack_start( self._component, expand=True )
# **********************************************************************************
def test_tagdata():
    import tag_data
    data = tag_data.TagDataTree()
    comp = tag_data.TagDataGadget( data )
    app = TestComponent( comp )
    app.run()
if __name__ == '__main__':
    test_tagdata()
# **********************************************************************************

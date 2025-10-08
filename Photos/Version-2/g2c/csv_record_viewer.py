#!/usr/bin/env python3
import wx
import csv
import os

class RecordViewerFrame(wx.Frame):
    def __init__(self, parent, title):
        super(RecordViewerFrame, self).__init__(
            parent, 
            title=title, 
            size=(500, 600),
            style=wx.DEFAULT_FRAME_STYLE  # Allow resizing
        )
        
        self.headers = []
        self.records = []
        self.current_record_idx = 0
        
        self.setup_ui()
        self.Centre()
        self.create_menu()
        self.bind_events()
        
        # Set default file path for testing
        self.default_csv_path = os.path.join(os.getcwd(), "data", "sample.csv")
        
    def setup_ui(self):
        # Main panel
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # Title
        title_font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title_text = wx.StaticText(self.panel, label="CSV Record Viewer")
        self.title_text.SetFont(title_font)
        self.main_sizer.Add(self.title_text, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Instructions
        instructions = wx.StaticText(
            self.panel, 
            label="Use ← and → arrow keys to navigate through records"
        )
        self.main_sizer.Add(instructions, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        
        # Record content panel with scrolling
        self.scroll_panel = wx.ScrolledWindow(self.panel, style=wx.VSCROLL | wx.WANTS_CHARS)
        self.scroll_panel.SetScrollRate(10, 10)  # Faster scroll rate
        # Set minimum size to ensure visibility
        self.scroll_panel.SetMinSize((450, 300))
        # Set background color to make panel visible
        self.scroll_panel.SetBackgroundColour(wx.Colour(240, 240, 250))
        
        # Ensure scroll panel can receive keyboard events
        self.scroll_panel.Bind(wx.EVT_SET_FOCUS, self.on_scroll_focus)
        self.record_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_panel.SetSizer(self.record_sizer)
        # Always show vertical scrollbar
        self.scroll_panel.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        
        # Placeholder message
        self.placeholder = wx.StaticText(
            self.scroll_panel, 
            label="No CSV file loaded. Use File > Open to select a file."
        )
        self.record_sizer.Add(self.placeholder, 0, wx.ALL, 20)
        
        # Add scroll panel to main sizer with expand flag to ensure it takes available space
        self.main_sizer.Add(self.scroll_panel, 1, wx.EXPAND | wx.ALL, 10)
        
        # Navigation status bar
        self.nav_status = wx.StaticText(self.panel, label="")
        self.nav_status.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.main_sizer.Add(self.nav_status, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        
        # Button panel
        btn_panel = wx.Panel(self.panel)
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Previous record button
        self.prev_btn = wx.Button(btn_panel, label="← Previous")
        self.prev_btn.Bind(wx.EVT_BUTTON, self.on_previous)
        btn_sizer.Add(self.prev_btn, 1, wx.RIGHT, 5)
        
        # Next record button
        self.next_btn = wx.Button(btn_panel, label="Next →")
        self.next_btn.Bind(wx.EVT_BUTTON, self.on_next)
        btn_sizer.Add(self.next_btn, 1, wx.LEFT, 5)
        
        # Disable buttons initially
        self.prev_btn.Disable()
        self.next_btn.Disable()
        
        btn_panel.SetSizer(btn_sizer)
        self.main_sizer.Add(btn_panel, 0, wx.EXPAND | wx.ALL, 10)
        
        self.panel.SetSizer(self.main_sizer)
    
    def create_menu(self):
        menu_bar = wx.MenuBar()
        
        # File menu
        file_menu = wx.Menu()
        open_item = file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open a CSV file")
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")
        
        menu_bar.Append(file_menu, "&File")
        self.SetMenuBar(menu_bar)
        
        # Bind events
        self.Bind(wx.EVT_MENU, self.on_open, open_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
    
    def bind_events(self):
        # Bind keyboard events for arrow key navigation - with debugging
        # Bind to the frame for better keyboard event capture
        self.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        # Also bind to the panel for redundant capture
        self.panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        # Bind to the scroll panel too
        self.scroll_panel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # Create accelerator table for keyboard shortcuts
        accel_tbl = wx.AcceleratorTable([
            (wx.ACCEL_NORMAL, wx.WXK_LEFT, wx.ID_BACKWARD),
            (wx.ACCEL_NORMAL, wx.WXK_RIGHT, wx.ID_FORWARD),
        ])
        self.SetAcceleratorTable(accel_tbl)
        
        # Bind accelerator events
        self.Bind(wx.EVT_MENU, self.on_previous, id=wx.ID_BACKWARD)
        self.Bind(wx.EVT_MENU, self.on_next, id=wx.ID_FORWARD)
        
        # Set initial focus and make it visible
        self.panel.SetFocus()
        self.panel.SetFocusIgnoringChildren()
        
        # For global key events, create a generic event handler
        self.keydown_event_handler = wx.EvtHandler()
        self.keydown_event_handler.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        wx.GetApp().Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        
        # Also make the frame handle all char events
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char_hook)
        
        # Add size event handler for proper resizing
        self.Bind(wx.EVT_SIZE, self.on_size)
        
        # Add idle event to ensure focus is maintained
        self.Bind(wx.EVT_IDLE, self.on_idle)
        
    def on_scroll_focus(self, event):
        """Handle focus events for the scroll panel"""
        print("Scroll panel received focus")
        # If we want to do anything special when scroll panel gets focus
        event.Skip()  # Continue with normal focus processing
    
    def on_key_down(self, event):
        key_code = event.GetKeyCode()
        print(f"Key pressed: {key_code}")
        
        if key_code == wx.WXK_LEFT:
            print("Left arrow key detected")
            self.show_previous_record()
            return  # Don't skip this event
        elif key_code == wx.WXK_RIGHT:
            print("Right arrow key detected")
            self.show_next_record()
            return  # Don't skip this event
        
        # Skip for other keys to allow normal processing
        event.Skip()
        
    def on_char_hook(self, event):
        """Additional event handler for character hook events"""
        key_code = event.GetKeyCode()
        print(f"Char hook key: {key_code}")
        
        if key_code == wx.WXK_LEFT:
            print("Left arrow key detected in char hook")
            self.show_previous_record()
        elif key_code == wx.WXK_RIGHT:
            print("Right arrow key detected in char hook")
            self.show_next_record()
        else:
            event.Skip()
            
    def on_idle(self, event):
        """Ensures focus is maintained properly during idle time"""
        # Process any pending events
        event.Skip()
    
    def on_previous(self, event):
        self.show_previous_record()
    
    def on_next(self, event):
        self.show_next_record()
    
    def show_previous_record(self):
        print("show_previous_record called")
        if self.current_record_idx > 0:
            self.current_record_idx -= 1
            self.display_current_record()
            # Enhanced focus management after navigation
            self.panel.SetFocus()
            try:
                self.panel.SetFocusIgnoringChildren()
            except AttributeError:
                pass  # Method not available, handled in ensure_focus
            wx.CallAfter(self.ensure_focus)
    
    def show_next_record(self):
        print("show_next_record called")
        if self.current_record_idx < len(self.records) - 1:
            self.current_record_idx += 1
            self.display_current_record()
            # Enhanced focus management after navigation
            self.panel.SetFocus()
            try:
                self.panel.SetFocusIgnoringChildren()
            except AttributeError:
                pass  # Method not available, handled in ensure_focus
            wx.CallAfter(self.ensure_focus)
            
    def ensure_focus(self):
        """Helper method to ensure focus is set correctly"""
        print("Ensuring proper focus")
        # Force focus to the main panel for key navigation
        self.panel.SetFocus()
        
        # Try to use SetFocusIgnoringChildren if available
        try:
            self.panel.SetFocusIgnoringChildren()
        except AttributeError:
            # Method not available in this wxPython version, use alternative approach
            # Make sure this panel has focus by clicking on it programmatically
            evt = wx.MouseEvent(wx.wxEVT_LEFT_DOWN)
            evt.SetEventObject(self.panel)
            wx.PostEvent(self.panel, evt)
            
            evt = wx.MouseEvent(wx.wxEVT_LEFT_UP)
            evt.SetEventObject(self.panel)
            wx.PostEvent(self.panel, evt)
    
    def on_open(self, event):
        wildcard = "CSV files (*.csv)|*.csv|All files (*.*)|*.*"
        with wx.FileDialog(
            self, "Open CSV file", wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as file_dialog:
            
            # Set initial directory to data folder if it exists
            if os.path.exists(self.default_csv_path):
                file_dialog.SetPath(self.default_csv_path)
            
            if file_dialog.ShowModal() == wx.ID_CANCEL:
                return  # User canceled
            
            # Get the selected file's path
            file_path = file_dialog.GetPath()
            self.load_csv_file(file_path)
    
    def load_csv_file(self, file_path):
        try:
            with open(file_path, 'r', newline='') as csv_file:
                csv_reader = csv.reader(csv_file)
                
                # Reset data
                self.headers = []
                self.records = []
                self.current_record_idx = 0
                
                # Get headers (first row)
                try:
                    self.headers = next(csv_reader)
                    print(f"Headers loaded: {len(self.headers)} columns")
                    print(f"First few headers: {self.headers[:3]}")
                except StopIteration:
                    wx.MessageBox("CSV file is empty.", "Error", wx.OK | wx.ICON_ERROR)
                    return
                
                # Read all records
                for row in csv_reader:
                    self.records.append(row)
                
                # Debug output
                record_count = len(self.records)
                print(f"Records loaded: {record_count}")
                if record_count > 0:
                    print(f"First record sample: {self.records[0][:min(3, len(self.records[0]))]}")
                
                # Check if there are any records
                if not self.records:
                    wx.MessageBox("CSV file has headers but no data.", "Warning", wx.OK | wx.ICON_WARNING)
                
                # Display first record if available
                self.display_current_record()
                
                # Update window title with filename
                self.SetTitle(f"CSV Record Viewer - {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Error loading CSV file: {str(e)}")
            wx.MessageBox(f"Error loading CSV file: {str(e)}", "Error", wx.OK | wx.ICON_ERROR)
    
    def display_current_record(self):
        print(f"Displaying record {self.current_record_idx + 1} of {len(self.records)}")
        
        # Start with a fresh scroll panel
        self.scroll_panel.DestroyChildren()
        
        # Create a new record sizer
        self.record_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scroll_panel.SetSizer(self.record_sizer)
        
        # Reset background color to ensure visibility
        self.scroll_panel.SetBackgroundColour(wx.Colour(240, 240, 250))
        
        # Add a header to confirm display is working
        header_text = wx.StaticText(
            self.scroll_panel,
            label=f"Record {self.current_record_idx + 1} of {len(self.records)}",
            style=wx.ALIGN_CENTER
        )
        header_text.SetBackgroundColour(wx.Colour(220, 220, 240))
        header_text.SetForegroundColour(wx.Colour(0, 0, 0))
        header_font = wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        header_text.SetFont(header_font)
        self.record_sizer.Add(header_text, 0, wx.EXPAND | wx.ALL, 5)
        
        if not self.headers:
            self.placeholder = wx.StaticText(
                self.scroll_panel, 
                label="No CSV file loaded. Use File > Open to select a file."
            )
            self.placeholder.SetForegroundColour(wx.Colour(200, 0, 0))  # Red text
            self.record_sizer.Add(self.placeholder, 0, wx.ALL, 20)
            self.nav_status.SetLabel("")
            self.prev_btn.Disable()
            self.next_btn.Disable()
            
            print("No headers found, displaying placeholder")
            self.update_layout()
            return
        
        # If we have records
        if self.records and len(self.records) > self.current_record_idx:
            print(f"Processing record with {len(self.headers)} columns")
            
            # Simplified approach - direct display without nested panels
            main_display = wx.Panel(self.scroll_panel, style=wx.BORDER_RAISED)
            main_display.SetBackgroundColour(wx.Colour(255, 255, 220))  # Light yellow
            main_display.SetMinSize((400, -1))  # Min width only, height determined by content
            # No fixed height to allow content to determine size
            
            # Use a static box for a clear border with improved styling
            box_sizer = wx.StaticBoxSizer(wx.VERTICAL, main_display, "Record Details")
            static_box = box_sizer.GetStaticBox()
            static_box.SetBackgroundColour(wx.Colour(230, 230, 235))
            static_box.SetForegroundColour(wx.Colour(30, 55, 90))  # Dark blue for title
            static_box.SetFont(wx.Font(11, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            
            # Get current record
            record = self.records[self.current_record_idx]
            print(f"Record length: {len(record)}")
            
            # Create a table-like layout with better columns
            # First, create a panel to hold the table
            table_panel = wx.Panel(main_display)
            table_panel.SetBackgroundColour(wx.Colour(250, 250, 250))
            
            # Create a vertical sizer for the table rows
            table_sizer = wx.BoxSizer(wx.VERTICAL)
            
            # Add scroll indicator if we have many fields
            if len(self.headers) > 10:
                scroll_info = wx.StaticText(
                    main_display, 
                    label=f"Scroll to view all {len(self.headers)} fields",
                    style=wx.ALIGN_CENTER
                )
                scroll_info.SetForegroundColour(wx.Colour(128, 0, 0))  # Dark red
                scroll_info.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_ITALIC, wx.FONTWEIGHT_NORMAL))
                box_sizer.Add(scroll_info, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
            
            # First, find the maximum label width needed to prevent truncation
            max_label_width = 0
            test_dc = wx.ScreenDC()
            for header in self.headers:
                # Use bold font for measurement
                test_dc.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                width, height = test_dc.GetTextExtent(header)
                max_label_width = max(max_label_width, width)
            
            # Calculate minimum width for label column - 1/3 of available width, at most
            visible_width = self.scroll_panel.GetClientSize().GetWidth()
            max_label_width_calculated = max_label_width + 40  # Add padding for ":" and spacing
            max_label_width_percent = min(max_label_width_calculated, visible_width / 3)
            
            # Calculate value column width - at least 2/3 of available width
            value_column_width = max(visible_width - max_label_width_percent - 40, visible_width * 2/3)
            
            print(f"Label width: {max_label_width_percent}, Value width: {value_column_width}")
            
            # Add clean, professional column headers
            header_panel = wx.Panel(table_panel)
            header_panel.SetBackgroundColour(wx.Colour(42, 74, 106))  # Professional dark blue
            header_sizer = wx.BoxSizer(wx.HORIZONTAL)
            
            # Create simpler, cleaner header labels
            field_header = wx.StaticText(header_panel, label="Field")
            field_header.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            field_header.SetForegroundColour(wx.Colour(255, 255, 255))  # White text
            
            value_header = wx.StaticText(header_panel, label="Value")
            value_header.SetFont(wx.Font(12, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
            value_header.SetForegroundColour(wx.Colour(255, 255, 255))  # White text
            
            # Add clean separator line at bottom of header
            def on_paint_header(event):
                dc = wx.PaintDC(header_panel)
                size = header_panel.GetSize()
                # Draw a single clean line at the bottom
                dc.SetPen(wx.Pen(wx.Colour(255, 255, 255), 1))  # White line
                dc.DrawLine(0, size.height - 1, size.width, size.height - 1)
            
            header_panel.Bind(wx.EVT_PAINT, on_paint_header)
            
            # Add field and value headers with proper spacing and alignment
            header_sizer.Add(field_header, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 12)
            
            # Calculate proper spacing between headers - ensure value is properly positioned
            first_col_width = max_label_width_percent
            header_sizer.AddSpacer(first_col_width - field_header.GetSize().width)
            
            value_position = first_col_width + 20  # Add some padding between columns
            header_sizer.Add(value_header, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 20)
            
            header_panel.SetSizer(header_sizer)
            
            # Add the header panel with sufficient bottom margin
            table_sizer.Add(header_panel, 0, wx.EXPAND)
            
            # Use a cleaner, more subtle separator approach
            separator_panel = wx.Panel(table_panel, size=(-1, 1))
            separator_panel.SetBackgroundColour(wx.Colour(200, 200, 220))  # Light gray separator
            table_sizer.Add(separator_panel, 0, wx.EXPAND)
            
            # Create label-value pairs in alternating rows for better readability
            for i, header in enumerate(self.headers):
                # Alternate row colors with more subtle distinction
                row_panel = wx.Panel(table_panel)
                if i % 2 == 0:
                    row_panel.SetBackgroundColour(wx.Colour(240, 240, 245))  # Very light blue-gray
                else:
                    row_panel.SetBackgroundColour(wx.Colour(250, 250, 255))  # White with slight blue tint
                
                row_sizer = wx.BoxSizer(wx.HORIZONTAL)
                
                # Label (field name) with enhanced styling
                label = wx.StaticText(row_panel, label=f"{header}:")
                label.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
                label.SetForegroundColour(wx.Colour(30, 55, 90))  # Darker blue that matches header theme
                
                # Set fixed width for field labels - 1/3 of panel width max
                visible_width = self.scroll_panel.GetClientSize().GetWidth()
                label_width = min(max_label_width_percent, visible_width / 3)
                label.SetMinSize((label_width, -1))
                
                # Value with improved wrapping and display
                value = ""
                if i < len(record):
                    value = record[i]
                
                # Create value in multiline style for longer text
                value_style = 0
                if len(value) > 60:  # For longer values
                    value_style = wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_NONE
                    value_text = wx.TextCtrl(row_panel, value=value, style=value_style)
                    value_text.SetBackgroundColour(row_panel.GetBackgroundColour())
                else:
                    value_text = wx.StaticText(row_panel, label=value)
                
                value_text.SetForegroundColour(wx.Colour(0, 0, 0))  # Black
                
                # Calculate proper wrapping width - give value column at least 60% of width
                visible_size = self.scroll_panel.GetClientSize()
                value_width = max(visible_size.GetWidth() * 0.6, visible_size.GetWidth() - label_width - 50)
                
                # Apply wrapping for StaticText or set size for TextCtrl
                if isinstance(value_text, wx.StaticText):
                    value_text.Wrap(int(value_width))
                else:
                    # For multiline text control
                    value_text.SetMinSize((int(value_width), -1))
                    
                    # Count lines needed and set height accordingly
                    line_count = value.count('\n') + 1
                    line_count = max(line_count, len(value) // 60 + 1)  # Estimate line breaks
                    line_height = value_text.GetCharHeight()
                    value_text.SetMinSize((int(value_width), line_height * min(line_count, 5) + 10))
                
                # Add to row with consistent layout but more space for value
                row_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.ALL, 5)
                row_sizer.Add(value_text, 1, wx.EXPAND | wx.ALL, 5)
                row_panel.SetSizer(row_sizer)
                
                # Add row to table with subtle border
                table_sizer.Add(row_panel, 0, wx.EXPAND | wx.BOTTOM, 1)
                
            
            # Finalize table panel
            table_panel.SetSizer(table_sizer)
            
            # Add the table to the main box sizer
            box_sizer.Add(table_panel, 1, wx.EXPAND | wx.ALL, 10)
            main_display.SetSizer(box_sizer)
            
            # Add to the main record sizer with EXPAND to allow it to grow as needed
            self.record_sizer.Add(main_display, 1, wx.EXPAND | wx.ALL, 10)
            
            # Add a bottom indicator if we have many fields
            if len(self.headers) > 20:
                bottom_indicator = wx.Panel(self.scroll_panel)
                bottom_indicator.SetBackgroundColour(wx.Colour(240, 240, 240))
                bottom_sizer = wx.BoxSizer(wx.VERTICAL)
                
                end_text = wx.StaticText(
                    bottom_indicator,
                    label="--- End of Record ---",
                    style=wx.ALIGN_CENTER
                )
                end_text.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                
                bottom_sizer.Add(end_text, 0, wx.ALIGN_CENTER | wx.ALL, 5)
                bottom_indicator.SetSizer(bottom_sizer)
                
                self.record_sizer.Add(bottom_indicator, 0, wx.EXPAND | wx.TOP, 5)
            
            # Print size information for debugging
            main_display_size = main_display.GetSize()
            print(f"Main display panel size: {main_display_size.width} x {main_display_size.height}")
            
            # Make sure the panel is shown
            main_display.Show(True)
            
            # Update navigation status
            self.nav_status.SetLabel(f"Record {self.current_record_idx + 1} of {len(self.records)}")
            
            # Enable/disable navigation buttons
            self.prev_btn.Enable(self.current_record_idx > 0)
            self.next_btn.Enable(self.current_record_idx < len(self.records) - 1)
        else:
            # No records, just headers
            no_records_text = wx.StaticText(
                self.scroll_panel, 
                label="No records found in the CSV file."
            )
            no_records_text.SetForegroundColour(wx.Colour(200, 0, 0))  # Red text
            self.record_sizer.Add(no_records_text, 0, wx.ALL, 20)
            self.nav_status.SetLabel("")
            self.prev_btn.Disable()
            self.next_btn.Disable()
        
        
        # Update layout
        self.update_layout()
    
    def update_layout(self):
        """Update layout of all panels to ensure proper display"""
        # Apply layout to child panels first
        for child in self.scroll_panel.GetChildren():
            if child.GetSizer():
                child.GetSizer().Layout()
                child.Fit()
        
        # Update the record sizer
        self.record_sizer.Layout()
        
        # Configure scroll panel with faster scrolling rate for large content
        self.scroll_panel.SetScrollRate(10, 10)
        self.scroll_panel.EnableScrolling(False, True)  # vertical scrolling only
        
        # Get the size of the content
        content_size = self.record_sizer.GetMinSize()
        
        # Get the visible size of the scroll panel
        visible_size = self.scroll_panel.GetClientSize()
        
        # Calculate virtual size - ensure it's at least as large as the content
        virtual_size = wx.Size(
            max(content_size.GetWidth(), visible_size.GetWidth()),
            max(content_size.GetHeight(), visible_size.GetHeight())
        )
        
        # Add some extra space to the virtual height if content is taller than visible area
        # This provides a visual cue that there's more content
        if content_size.GetHeight() > visible_size.GetHeight():
            # Add some padding to make it clear there's more content
            virtual_size.SetHeight(virtual_size.GetHeight() + 20)
            print(f"Content extends beyond visible area: {content_size.GetHeight()} > {visible_size.GetHeight()}")
        
        # Make sure virtual size is at least a minimum width to maintain readability
        if virtual_size.GetWidth() < 450:
            virtual_size.SetWidth(450)
            
        # Set the virtual size
        self.scroll_panel.SetVirtualSize(virtual_size)
        print(f"Virtual size set to: {virtual_size.GetWidth()} x {virtual_size.GetHeight()}")
        
        # Make sure scrollbars show when needed
        self.scroll_panel.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_ALWAYS)
        
        # Refresh scroll panel and ensure content fits
        self.scroll_panel.FitInside()
        self.scroll_panel.Refresh()
        
        # Update main panel layout
        self.main_sizer.Layout()
        self.panel.Layout()
        self.panel.Refresh()
        self.panel.Update()
        
        # Set focus to panel to enable keyboard navigation - enhanced version
        self.panel.SetFocus()
        
        # Use SetFocusIgnoringChildren only if it exists in this wxPython version
        try:
            self.panel.SetFocusIgnoringChildren()
        except AttributeError:
            # Fall back to regular SetFocus if the method doesn't exist
            pass
        
        # Make focus visible to the user
        self.panel.SetBackgroundColour(wx.Colour(245, 245, 255))  # Subtle focus color
        wx.CallAfter(self.ensure_focus)
    
    def on_size(self, event):
        """Handle window resize events"""
        # Get the new size
        frame_size = self.GetSize()
        
        # Update the scroll panel to fill the available space
        # (This will be managed by the sizer, but we ensure it's updated)
        self.Layout()
        
        # Make sure virtual size is appropriate for content
        if self.record_sizer:
            # Get the content size
            content_size = self.record_sizer.GetMinSize()
            
            # Get the visible client area size
            visible_size = self.scroll_panel.GetClientSize()
            
            # Virtual size must accommodate content
            virtual_size = wx.Size(
                max(content_size.GetWidth(), visible_size.GetWidth()),
                content_size.GetHeight()  # Height based on actual content
            )
            
            # Set the virtual size and refresh
            self.scroll_panel.SetVirtualSize(virtual_size)
            self.scroll_panel.FitInside()
            
            print(f"Resize event: Frame size={frame_size.GetWidth()}x{frame_size.GetHeight()}, " +
                  f"Content size={content_size.GetWidth()}x{content_size.GetHeight()}, " +
                  f"Virtual size={virtual_size.GetWidth()}x{virtual_size.GetHeight()}")
        
        # Continue with default processing
        event.Skip()
    
    def on_exit(self, event):
        self.Close()

class RecordViewerApp(wx.App):
    def OnInit(self):
        frame = RecordViewerFrame(None, "CSV Record Viewer")
        frame.Show()
        # Ensure the frame has focus initially
        frame.SetFocus()
        # Bind application-level key events
        self.Bind(wx.EVT_KEY_DOWN, frame.on_key_down)
        return True
        
    def FilterEvent(self, event):
        """Override to catch key events at application level"""
        if event.GetEventType() == wx.wxEVT_KEY_DOWN:
            print("App level key event")
            # Let the normal processing occur as well
        return -1  # Continue processing

if __name__ == "__main__":
    app = RecordViewerApp()
    
    # Create a global event filter for key events
    class GlobalEventFilter(wx.EvtHandler):
        def __init__(self, frame):
            super(GlobalEventFilter, self).__init__()
            self.frame = frame
            
        def ProcessEvent(self, event):
            if event.GetEventType() == wx.wxEVT_KEY_DOWN:
                key_code = event.GetKeyCode()
                print(f"Global filter key: {key_code}")
                if key_code == wx.WXK_LEFT:
                    self.frame.show_previous_record()
                    return True
                elif key_code == wx.WXK_RIGHT:
                    self.frame.show_next_record()
                    return True
            return super(GlobalEventFilter, self).ProcessEvent(event)
    
    # Get the first frame
    frame = None
    for window in wx.GetTopLevelWindows():
        if isinstance(window, RecordViewerFrame):
            frame = window
            break
            
    if frame:
        try:
            # Create and install the event filter
            filter = GlobalEventFilter(frame)
            # Use version-safe approach to enable the event handler 
            if hasattr(wx.EvtHandler, 'SetEvtHandlerEnabled'):
                wx.EvtHandler.SetEvtHandlerEnabled(filter, True)
            
            # Use version-safe approach for capture window
            if hasattr(app, 'SetCaptureWindow'):
                app.SetCaptureWindow(frame)
        except Exception as e:
            print(f"Warning: Event filter setup failed: {e}")
            # Continue without the global event filter
        
    app.MainLoop()


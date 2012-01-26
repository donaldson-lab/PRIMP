import wx
import Assembly
import Grid
import matplotlib.pyplot as plt

white = (255,255,255)
red = (255,0,0)
light_red = (255,100,100)
green = (0,225,50)
light_green = (150,255,150)
blue = (0,0,255)
light_blue = (100,100,255)
brown = (155,100,0)
gold = (255,215,0)
yellow = (255,255,150)
black = (0,0,0)
light_black = (50,50,50)

# uses Matplotlib to generate a scatter plot of the shannon entropy
# of non-deleted positions in an assembly
class ShannonChart():
    
    def __init__(self,assembly):
        self.Generate(assembly,'o','shannon plot')
    
    # generate the plot. shape is the plot symbol
    def Generate(self,assembly,shape,title):
        
        x,samples = assembly.get_shannon()
        num_samples = len(samples)

        color_list = ['r','b','g','y','m']
        label_list = []
        plt.plot(x,samples,color_list[0]+shape,label='position')
        plt.ylim(0,0.35)
        plt.title(title,fontsize=24)
        plt.xlabel('Position',fontsize=24)
        plt.ylabel('Shannon Entropy Value',fontsize=24)
        plt.legend()
        plt.show()

# do not use directly
class DisplayChart(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent = parent
        self.width,self.height = self.GetSizeTuple()
        self.BufferBitMap = wx.EmptyBitmap(self.width,self.height)
        self.start = (15,15)
        self.view_width = 0
        self.view_height = 0
    
    # to be called when the bar chart needs to be drawn
    def bindings(self):
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)    
    
    def OnSize(self,event):
        self.width,self.height = self.GetSizeTuple()
        self.BufferBitMap = wx.EmptyBitmap(self.width,self.height)
        memdc = wx.MemoryDC()
        memdc.SelectObject(self.BufferBitMap)
        self.DisplayBoundary(memdc)
        self.render(memdc)
    
    def OnPaint(self,event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.BufferBitMap,0,0,True)
        dc.EndDrawing()
    
    def DisplayBoundary(self,dc):
        self.view_height = self.height - 2*self.start[1]
        self.view_width = self.width - 2*self.start[0]
        
        dc.SetBrush(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND)))
        dc.DrawRectangle(0,0,self.width,self.height)
        
        dc.SetPen(wx.Pen(black, 1))
        dc.DrawLine(0,0,self.start[0],self.start[1])
        dc.DrawLine(self.width,0,self.width - self.start[0],self.start[1])
        dc.DrawLine(self.width,self.height,self.width - self.start[0] - 1,self.height - self.start[1] - 1)
        dc.DrawLine(0,self.height,self.start[0] + 1,self.height - self.start[1] - 1)
        dc.SetBrush(wx.Brush(white))
        dc.DrawRectangle(self.start[0],self.start[1],self.view_width,self.view_height)
        
class CoverageChart(DisplayChart):
    def __init__(self,parent,assembly):
        DisplayChart.__init__(self,parent)
        self.Assembly = assembly
        self.current_column = 0
        
    def bindings(self):
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN,self.coverage_position)
        
    def render(self,dc):
        
        dc.BeginDrawing()
        char_width = dc.GetFont().GetPixelSize().GetWidth()
        char_height = dc.GetFont().GetPixelSize().GetHeight()
        
        self.coverage_top = (self.start[0] + char_height,self.start[1] + char_height)
        self.coverage_width = self.view_width - 2*(self.coverage_top[0] - self.start[0])
        self.coverage_height = self.view_height - 2*(self.coverage_top[1] - self.start[1])
        
        dc.SetPen(wx.Pen(black, 2))
        dc.DrawRectangle(self.coverage_top[0],self.coverage_top[1],self.coverage_width,self.coverage_height)
        
        dc.DrawText(str(self.Assembly.max_coverage),self.coverage_top[0],self.coverage_top[1] - char_height)
        self.length = self.Assembly.length_of_consensus - self.Assembly.error_number
        dc.DrawText(str(self.length),self.coverage_top[0]+self.coverage_width - char_width*len(str(self.length)),self.coverage_top[1]+self.coverage_height)
    
        base = self.height - self.coverage_top[1]
        
        first_x = self.coverage_top[0]
        first_y = base - self.coverage_height*(float(self.Assembly.assembly[self.current_column][6])/self.Assembly.max_coverage)
        
        for i in range(0,len(self.Assembly.assembly)):
            if self.Assembly.assembly_stats[i][1] == True:
                continue
            second_x = first_x + float(self.coverage_width)/self.length
            second_y = base - self.coverage_height*(float(self.Assembly.assembly[i][6])/self.Assembly.max_coverage)
            dc.DrawLine(first_x,first_y,second_x,second_y)
            first_x = second_x
            first_y = second_y
        
        if self.Assembly.assembly_stats[self.current_column][0]==True:
            dc.SetPen(wx.Pen(blue,2))
        elif self.Assembly.assembly_stats[self.current_column][2]==True:
            dc.SetPen(wx.Pen(red,2))
        else:
            dc.SetPen(wx.Pen(gold,2))
            
        error_position = self.Assembly.assembly[self.current_column][7] # this is overkill if below method is called
        x = self.coverage_top[0] + self.coverage_width*(float(error_position+1)/self.length)
        dc.DrawLine(x,self.coverage_top[1] + 2,x,base - 2)
        dc.DrawText("Position: " + str(error_position),self.coverage_top[0],self.coverage_top[1] + self.coverage_height)
        dc.EndDrawing()
        
    # called when user clicks on the coverage chart
    def coverage_position(self,event):
        coor = event.GetPosition()
        error_position = 0
        if coor[0]<self.coverage_top[0] or coor[0] > self.coverage_top[0] + self.coverage_width or coor[1] < self.coverage_top[1] or coor[1] > self.coverage_top[1] + self.coverage_height:
            return False
        else:
            error_position = int(self.length*(float(coor[0] - self.coverage_top[0])/self.coverage_width))
        if error_position < 0:
            error_position = 0
        if error_position > self.length - 1:
            error_position = self.length - 1
        column = self.Assembly.get_position_column(error_position)
        self.parent.display_column(column)

class BarChart(DisplayChart):
    def __init__(self,parent):
        DisplayChart.__init__(self,parent)
        
    def set_assembly(self,assembly):
        self.assembly = assembly
        
    def set_column(self,column):
        self.column = column
        
    def draw_bar(self,dc,letter,position,bar_width):
            char_height = dc.GetFont().GetPixelSize().GetHeight()
            char_width = dc.GetFont().GetPixelSize().GetWidth()
            percent = float(self.assembly.assembly[self.column][letter])/self.assembly.assembly[self.column][6]
            if percent > 0.0:
                bar_height = int(self.chart_height*(percent))
                dc.DrawRectangle(self.chart_top[0] + position*bar_width + bar_width/8.0,self.chart_top[1] + self.chart_height - bar_height,3.0*bar_width/4.0,bar_height)
                string_offset = (char_width/2)*len(str(int(self.assembly.assembly[self.column][letter])))/2
                dc.DrawText(str(int(self.assembly.assembly[self.column][letter])),self.chart_top[0]  + (2*position+1)*bar_width/2.0 - string_offset,self.base - char_height)
            else:
                dc.DrawText("0",self.chart_top[0]  + (2*position+1)*bar_width/2.0,self.base - char_height)
        
    def render(self,dc):
        color = gold
        if self.assembly.assembly_stats[self.column][2]==True:
            color = red
        elif self.assembly.assembly_stats[self.column][0]==True:
            color = blue
        else:
            pass
        

        self.chart_top = [2*i for i in self.start]
        self.chart_width = self.width - 2*self.chart_top[0]
        self.chart_height = self.height - 2*self.chart_top[1]
        self.base = self.chart_top[1] + self.chart_height
        dc.DrawRectangle(self.chart_top[0],self.chart_top[1],self.chart_width,self.chart_height)
        
        bar_width = self.chart_width/5.0
        
        dc.SetPen(wx.Pen(green, 0))
        dc.SetBrush(wx.Brush(green))

        if self.assembly.assembly[self.column][6]>0:
            self.draw_bar(dc,0,0.0,bar_width)
            self.draw_bar(dc,1,1.0,bar_width)
            self.draw_bar(dc,2,2.0,bar_width)
            self.draw_bar(dc,3,3.0,bar_width)
            self.draw_bar(dc,4,4.0,bar_width)
        
        dc.DrawText("A",bar_width/2.0 + self.chart_top[0],self.base)
        dc.DrawText("C",3.0*bar_width/2.0 + self.chart_top[0],self.base)
        dc.DrawText("T",5.0*bar_width/2.0 + self.chart_top[0],self.base)
        dc.DrawText("G",7.0*bar_width/2.0 + self.chart_top[0],self.base)
        dc.DrawText("-",9.0*bar_width/2.0 + self.chart_top[0],self.base)
        dc.EndDrawing()

## Control for viewing and editing assemblies
class Control(wx.Panel):

    def __init__(self,frame,assembly_file):
        wx.Panel.__init__(self,frame)
        
        # non-panel objects
        self.Assembly = None
        self.Grid = None
        self.Assembly_File = assembly_file
        
    def set_panels(self):
        self.construct_toolbar()
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.grid_panel = wx.Panel(self,-1,wx.DefaultPosition,wx.DefaultSize,wx.SUNKEN_BORDER)
        self.grid_sizer = wx.BoxSizer(wx.VERTICAL)
        self.Grid = Grid.AssemblyGrid(self)
        self.Grid.show_assembly(self.Assembly)
        self.grid_bindings()
        self.grid_sizer.Add(self.Grid,1,wx.EXPAND)
        self.grid_panel.SetSizer(self.grid_sizer)
        self.grid_panel.SetMinSize((0,self.Grid.get_height() + 18))
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bar_panel = BarChart(self)
        self.bar_panel.set_assembly(self.Assembly)
        self.bar_panel.set_column(0)
        self.bar_panel.bindings()
        self.coverage_panel = CoverageChart(self,self.Assembly)
        self.coverage_panel.bindings()
        self.bottom_sizer.Add(self.bar_panel,1,wx.EXPAND)
        self.bottom_sizer.Add(self.coverage_panel,1,wx.EXPAND)
        self.sizer.Add(self.grid_panel,0,wx.EXPAND)
        self.sizer.Add(self.bottom_sizer,1,wx.EXPAND)
        self.SetSizer(self.sizer)
    
    # Initial Display    
    def OpenAceFile(self,snp_parameter,error_parameter):
        self.Assembly = Assembly.Assembly()
        self.Assembly.open(snp_parameter,error_parameter,self.Assembly_File)
        
    def grid_bindings(self):
        self.Grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK,self.cell_clicked)
        self.Grid.Bind(wx.grid.EVT_GRID_LABEL_LEFT_CLICK,self.cell_clicked)
        self.Grid.Bind(wx.EVT_KEY_DOWN,self.arrow_keys)
        self.Grid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK,self.edit_cell)
        
    def display_column(self,column):
        self.Grid.SetFocus()
        self.Grid.display_column(column)
        self.bar_panel.set_column(column)
        self.bar_panel.OnSize(0)
        self.coverage_panel.current_column = column
        self.coverage_panel.OnSize(0)
        self.Refresh()
    
    def arrow_keys(self,event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_LEFT:
            self.Grid.move_left()
            self.display_column(self.Grid.current_column)
        elif keycode == wx.WXK_RIGHT:
            self.Grid.move_right()
            self.display_column(self.Grid.current_column)
        else:
            pass 
    
    def edit_cell(self,event):
        selected_column = self.Grid.edit_cell(event)
        self.Bind(wx.grid.EVT_GRID_CELL_CHANGE,lambda event: self.change_cell(event,selected_column))
        
    def change_cell(self,event,selected_column):
        self.Assembly.change_column(selected_column,self.Grid.GetCellValue(0,selected_column))
        self.display_column(selected_column)
        
    def cell_clicked(self,event):
        selected_column = event.GetCol()
        self.display_column(selected_column)
    
    def previous_item(self,type):
        if type==0:
            previous = self.Assembly.previous_gap(self.Grid.current_column)
            self.display_column(previous)
        elif type == 2:
            previous = self.Assembly.previous_snp(self.Grid.current_column)
            self.display_column(previous)
        
    def next_item(self,type):
        if type==0:
            next = self.Assembly.next_gap(self.Grid.current_column)
            self.display_column(next)
        elif type == 2:
            next = self.Assembly.next_snp(self.Grid.current_column)
            self.display_column(next)
        
    def delete_column(self,event):
        selected_column = event.GetCol()
        self.Assembly.delete_column(selected_column)
        self.Grid.delete_column(selected_column)
        self.display_column(self.Grid.current_column)
        # push column to undo stack
    
    def find_column(self,position):
        for i in range(0,len(self.Assembly.assembly)):
            if self.Assembly.assembly[i][7] == position:
                self.display_column(i)
    
    def delete_column(self,event):
        self.Grid.delete_column(self.Grid.current_column)
        self.Assembly.delete_column(self.Grid.current_column)
        
    def construct_toolbar(self):
        parent = self.GetParent()
        
        if parent.has_toolbar == 1:
            parent.toolbar.Destroy()
        
        self.toolbar = parent.CreateToolBar(wx.TB_HORZ_LAYOUT | wx.TB_TEXT)
        parent.has_toolbar = 1
        parent.toolbar = self.toolbar
        
        self.toolbar.AddSeparator()
        
        gap_arrow_left_image = wx.EmptyImage(15,15)
        gap_arrow_left_image.LoadFile("left_blue.png",wx.BITMAP_TYPE_PNG)
        gap_arrow_left = gap_arrow_left_image.ConvertToBitmap()
        
        gap_arrow_right_image = wx.EmptyImage(15,15)
        gap_arrow_right_image.LoadFile("right_blue.png",wx.BITMAP_TYPE_PNG)
        gap_arrow_right = gap_arrow_right_image.ConvertToBitmap()
        
        snp_arrow_left_image = wx.EmptyImage(15,15)
        snp_arrow_left_image.LoadFile("left_red.png",wx.BITMAP_TYPE_PNG)
        snp_arrow_left = snp_arrow_left_image.ConvertToBitmap()
        
        snp_arrow_right_image = wx.EmptyImage(15,15)
        snp_arrow_right_image.LoadFile("right_red.png",wx.BITMAP_TYPE_PNG)
        snp_arrow_right = snp_arrow_right_image.ConvertToBitmap()
        
        """
        for i in range(0,32):
            for j in range(0,32):
                if snp_arrow_left_image.GetBlue(i,j) > 0:
                    snp_arrow_left_image.SetRGB(i,j,snp_arrow_left_image.GetBlue(i,j),snp_arrow_left_image.GetGreen(i,j)/2.5,snp_arrow_left_image.GetRed(i,j)/1.2 )
        snp_arrow_left_image.SaveFile("left_red",wx.BITMAP_TYPE_PNG)
        snp_arrow_left = snp_arrow_left_image.ConvertToBitmap()
        """
        
        delete_image = wx.EmptyImage(15,15)
        delete_image.LoadFile("delete.png",wx.BITMAP_TYPE_PNG)
        delete_icon = delete_image.ConvertToBitmap()
        
        self.toolbar.AddLabelTool(1,'Previous SNP',snp_arrow_left)
        self.toolbar.AddLabelTool(2,'Next SNP',snp_arrow_right)
        self.toolbar.AddLabelTool(5,'Previous Gap',gap_arrow_left)
        self.toolbar.AddLabelTool(6,'Next Gap',gap_arrow_right)
        self.toolbar.AddLabelTool(4,'Delete Column',delete_icon)

        find_position_label = wx.StaticText(self.toolbar,-1,"Find Position:",style=wx.ALIGN_BOTTOM)
        find_position_text = wx.TextCtrl(self.toolbar,style=wx.TE_PROCESS_ENTER | wx.ALIGN_BOTTOM)
        self.toolbar.AddControl(find_position_label)
        self.toolbar.AddControl(find_position_text)
        self.toolbar.Realize()
        
        parent.Bind(wx.EVT_TOOL,lambda event: self.previous_item(0),id=5)
        parent.Bind(wx.EVT_TOOL,lambda event: self.next_item(0),id=6)
        parent.Bind(wx.EVT_TOOL,lambda event: self.previous_item(2),id=1)
        parent.Bind(wx.EVT_TOOL,lambda event: self.next_item(2),id=2)
        parent.Bind(wx.EVT_TOOL,self.delete_column,id=4)
        find_position_text.Bind(wx.EVT_TEXT_ENTER,lambda event: self.find_column(int(find_position_text.GetValue())))

class MainFrame(wx.Frame):
    def __init__(self,parent,title):
        wx.Frame.__init__(self,parent,title=title,size=(800,400))
        self.current_panel = wx.Panel(self,-1)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.current_panel,1,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.has_toolbar = 0
        self.menu()
        self.Center()
        self.Show()
        
    def menu(self):
        self.file_menu()
        self.edit_menu()
        self.find_menu()
        self.view_menu()
        
        self.Menu_Bar = wx.MenuBar()
        self.Menu_Bar.Append(self.File_Menu,"&File")
        self.Menu_Bar.Append(self.Edit_Menu,"&Edit")
        self.Menu_Bar.Append(self.Find_Menu,"&Find")
        self.Menu_Bar.Append(self.View_Menu,"&View")
        self.SetMenuBar(self.Menu_Bar)
    
    def file_menu(self):
        self.File_Menu = wx.Menu()
        self.New_Menu_Item = self.File_Menu.Append(101,"&New")
        self.Open_Menu_Item = self.File_Menu.Append(102,"&Open Saved Project")
        
        self.File_Menu.AppendSeparator()
        
        self.Save_Consensus_Item = self.File_Menu.Append(103,"&Save Consensus")
        self.Save_Info_Item = self.File_Menu.Append(104,"&Save Info")
        self.Save_Project_Menu_Item = self.File_Menu.Append(105,"&Save Project")
        self.Save_Info_Item.Enable(False)
        self.Save_Consensus_Item.Enable(False)
        self.Save_Project_Menu_Item.Enable(False)
        
        self.File_Menu.AppendSeparator()
        
        self.Exit_Menu_Item = self.File_Menu.Append(106,"E&xit","Quit")
        
        self.Bind(wx.EVT_MENU,self.open_dialog,id=101)
        #self.Bind(wx.EVT_MENU,lambda event: self.open_dialog(self.open_project,[],".asmb",1),id=102)
        #self.Bind(wx.EVT_MENU,lambda event: self.save_dialog(self.save_consensus),id=103)
        #self.Bind(wx.EVT_MENU,lambda event: self.save_dialog(self.save_info),id=104)
        #self.Bind(wx.EVT_MENU,lambda event: self.save_dialog(self.save_project),id=105)
        #self.Bind(wx.EVT_MENU,self.close,id=106)
        
    def edit_menu(self):
        self.Edit_Menu = wx.Menu()
        self.Undo_Item = self.Edit_Menu.Append(201,"&Undo","Undo")
        self.Undo_Item.Enable(False)
        self.Recalculate_Item = self.Edit_Menu.Append(202,"&Recalculate SNP's","Recalculate SNPs")
        self.Recalculate_Item.Enable(False)
        
        #self.Bind(wx.EVT_MENU,self.undo_control,id=201)
        #self.Bind(wx.EVT_MENU,self.recalculate_snp_display,id=202)
        
    def find_menu(self):
        self.Find_Menu = wx.Menu()
        self.Find_SNP_Item = self.Find_Menu.Append(301,"&SNP's","SNP List")
        self.Find_SNP_Item.Enable(False)
        self.Find_Gap_Item = self.Find_Menu.Append(302,"&Gaps","Gap List")
        self.Find_Gap_Item.Enable(False)
        
        #self.Bind(wx.EVT_MENU,self.find_snp,id=301)
        #self.Bind(wx.EVT_MENU,self.find_gap,id=302)
        
    def view_menu(self):
        self.View_Menu = wx.Menu()
        
        self.Open_Info_Menu_Item = self.View_Menu.Append(401,"&Open Consensus Chart")
        self.Open_Info_Menu_Item.Enable(False)
        
        self.View_Menu.AppendSeparator()
        
        self.Shannon_Item = self.View_Menu.Append(402,"&Shannon Entropy")
        self.Shannon_Item.Enable(False)
        self.RMSD_Item = self.View_Menu.Append(403,"RMSD")
        self.RMSD_Item.Enable(False)
        
        self.View_Menu.AppendSeparator()

        #self.Bind(wx.EVT_MENU,self.consensus_chart,id=401)
        self.Bind(wx.EVT_MENU,lambda event: ShannonChart(self.Control.Assembly),id=402)
        #self.Bind(wx.EVT_MENU,lambda event: RMSDChart(self,self.data,self.grid),id=403)
        
    def enable_menu_items(self,b):
        self.Save_Consensus_Item.Enable(b)
        self.Save_Info_Item.Enable(b)
        self.Save_Project_Menu_Item.Enable(b)
        self.Recalculate_Item.Enable(b)
        self.Find_SNP_Item.Enable(b)
        self.Find_Gap_Item.Enable(b)
        self.Open_Info_Menu_Item.Enable(b)
        self.Shannon_Item.Enable(b)
        self.RMSD_Item.Enable(b)
        
    def clear_panels(self,show_panel):
        self.sizer.Replace(self.current_panel,show_panel)
        self.current_panel.Hide()
        self.current_panel = show_panel
        show_panel.Refresh()
        show_panel.Layout()
        self.Layout()
        self.Refresh()
    
    def parameter_box(self,assembly_file):
        
        parameter_panel = wx.Panel(self,-1)
        
        parameter_box = wx.BoxSizer(wx.VERTICAL)
        
        title_label = wx.StaticBox(parameter_panel,-1,"Parameters:")
        title_label_sizer = wx.StaticBoxSizer(title_label,wx.VERTICAL)
        
        error_label = wx.StaticText(parameter_panel, -1, "Enter Error Percentage:")
        error_text = wx.TextCtrl(parameter_panel, -1, "0.75", size=(175, -1))
        error_text.SetInsertionPoint(0)
        
        snp_label = wx.StaticText(parameter_panel, -1, "Enter SNP Percentage:")
        snp_text = wx.TextCtrl(parameter_panel, -1, "0.10", size=(175, -1))
        
        sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)
        sizer.AddMany([error_label, error_text, snp_label, snp_text])
        title_label_sizer.Add(sizer,1,wx.CENTER)
        
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer_h = wx.BoxSizer(wx.HORIZONTAL)
        button = wx.Button(parameter_panel,1,"Enter")
        button_sizer_h.Add(button,1,wx.CENTER)
        button_sizer.Add(button_sizer_h,1,wx.CENTER)

        parameter_box.Add(title_label_sizer,4,wx.CENTER)
        parameter_box.Add(button_sizer,1,wx.CENTER)
        
        parameter_panel.SetSizer(parameter_box)
        
        button.Bind(wx.EVT_BUTTON,lambda event: self.open_assembly(float(snp_text.GetValue()),float(error_text.GetValue()),assembly_file) )
        
        self.clear_panels(parameter_panel)
    
    def open_dialog(self,event):
        filedlg = wx.FileDialog(self,"Please Choose File","","", "*", wx.OPEN)
        if filedlg.ShowModal() == wx.ID_OK:
            self.parameter_box(filedlg.GetPath())
        filedlg.Destroy()
    
    def open_assembly(self,snp_parameter,error_parameter,assembly_file):
        self.enable_menu_items(True)
        self.Control = Control(self,assembly_file)
        self.Control.OpenAceFile(snp_parameter,error_parameter)
        self.Control.set_panels()
        self.clear_panels(self.Control)
    
    def construct_status(self):
        self.CreateStatusBar()
        self.SetStatusText("Click Cell for Position")
                        
    def close(self,event):
        self.Destroy()

def main():
    app = wx.App(False)
    Frame = MainFrame(None, "PRIMP")              
    app.MainLoop()              

if __name__ == "__main__":
    main()
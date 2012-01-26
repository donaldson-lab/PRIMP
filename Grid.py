'''
Created on Aug 13, 2010

@author: virushunter1
'''

import wx
import wx.grid
red = (255,0,0)
blue = (0,0,255)
brown = (155,100,0)
gold = (255,215,0)
black = (0,0,0)
column_width = 15

class AssemblyGrid(wx.grid.Grid):
    def __init__(self,frame):
        wx.grid.Grid.__init__(self,frame)
        self.rowsize = 0
        self.colsize = 0
        self.current_column = 0
        self.column_width = 15
        
    def get_height(self):
        col_label_height = self.GetColLabelSize()
        row_height_1 = self.GetRowSize(0)
        row_height_2 = self.GetRowSize(1)
        return col_label_height + row_height_1 + row_height_2

    def show_assembly(self,assemb):
        self.Assembly = assemb
        self.show_grid(2,self.Assembly.length_of_consensus)
    
    def show_grid(self,rowsize,colsize):
        assert rowsize > 0
        assert rowsize > 0
        
        self.rowsize = rowsize
        self.colsize = colsize
        
        self.CreateGrid(self.rowsize,self.colsize)
        self.SetMargins(0,0)
        self.DisableDragColSize()
        self.SetCellHighlightPenWidth(0)
        self.SetColLabelSize(0)
        self.SetColMinimalAcceptableWidth(0)

        self.SetRowLabelValue(0,self.Assembly.consensus_name)
        self.SetRowLabelValue(1,self.Assembly.reference_name)
        if (len(self.Assembly.consensus_name) > len(self.Assembly.reference_name) ):
            self.SetRowLabelSize(len(self.Assembly.consensus_name)*self.GetFont().GetPointSize())
        else:
            self.SetRowLabelSize(len(self.Assembly.reference_name)*self.GetFont().GetPointSize())
        
        for col in range(0,self.colsize):
            self.SetColMinimalWidth(col,0)
            self.SetColLabelValue(col,"")

            if self.Assembly.assembly_stats[col][3] == True: # case when column is deleted
                self.SetCellValue(0,col,"")
                self.SetCellValue(1,col,"")
                self.SetColSize(col,0)
            else:
                self.SetColSize(col,self.column_width)
                self.SetCellValue(0,col,self.Assembly.consensus[col])
                self.SetCellValue(1,col,self.Assembly.reference[col])
                self.SetColSize(col,self.column_width)
                if self.Assembly.assembly_stats[col][0] == True:
                    self.SetCellTextColour(0,col,blue)
                elif self.Assembly.assembly_stats[col][2] == True:
                    self.SetCellTextColour(0,col,red)
                else:
                    pass
            
    # Generic display position method. Does it even need a parameter?
    def display_column(self,column):
        self.current_column = column
        self.ClearSelection()
        self.SetGridCursor(0,self.current_column)
        self.SelectCol(column,True)
        self.MakeCellVisible(0,column)
        self.get_color(column)
        
    def get_color(self,column):
        if self.Assembly.assembly_stats[column][0]==True:
            self.SetSelectionBackground(blue)
        elif self.Assembly.assembly_stats[column][2]==True:
            self.SetSelectionBackground(red)
        else:
            self.SetSelectionBackground(gold)

    def delete_column(self,selected_column):
        self.SetCellValue(0,selected_column,"")
        self.SetCellValue(1,selected_column,"")
        self.SetColSize(selected_column,0)
    
    # undo a column delete    
    def undo_column(self,column):
        self.SetCellValue(0,column,self.consensus[column])
        self.SetColSize(selected_column,self.column_width)
        self.ForceRefresh()
    
    def move_left(self):
        if self.current_column == 0:
            self.current_column = self.GetNumberCols() - 1
        else:
            self.current_column = self.current_column - 1
        
    def move_right(self):
        if self.current_column == self.GetNumberCols()-1:
            self.current_column = 0
        else: 
            self.current_column = self.current_column + 1
    
    # Allow *Consensus* to be edited
    def edit_cell(self,event):
        self.ClearSelection()
        col = event.GetCol()
        self.current_column = col
        self.SetGridCursor(0,col)
        self.EnableCellEditControl(True)
        return col
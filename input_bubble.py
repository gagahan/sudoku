from kivy.lang import Builder

from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import BooleanProperty, ListProperty


import math
import numpy as np

NBLOCK_SCALE = 1.5

BTN_TXT_COL_INACTIVE = (.1, .1, .1, .8)
BTN_TXT_COL_ACTIVE = (1, 1, 1, .8)

UNDO_BTN_TXT = 'u'
REDO_BTN_TXT = 'r'
CLR_BTN_TXT = 'c'
SOLVE_BTN_TXT = 's'
HINT_BTN_TXT = 'h'
SHOW_CAN_BTN_TXT = '#'

class B_Btn(BubbleButton):
    
    txt_col_active = BTN_TXT_COL_ACTIVE
    txt_col_inactive = BTN_TXT_COL_INACTIVE
    active = BooleanProperty(False)
    supressed = BooleanProperty(False)
    
    def __init__(self, field, idx=0, **kwargs):
        self.field = field
        self.grid = field.grid
        self.index = idx        
        super(B_Btn, self).__init__(**kwargs)
        self.activate()
        
    def activate(self):
        raise NotImplementedError('activate-function must be defined')

    
class Val_Btn(B_Btn):
        
    def on_press(self):
        if self.active:
            self.grid.controller.set_value(self.field.index, self.index + 1)
            self.grid.bubble.update_btns()
            #self.grid.bubble.goodbye()
    
    def activate(self):
        '''
        wrong candidates depression must be implemented here!!
        '''
        # if auto-cand mode
        if not self.grid.candidate_exist(self.field.index, self.index + 1):
            self.supressed = True
            
        if not self.supressed:
            self.active = True
          
class Candidate_Btn(Val_Btn):
        
    def on_press(self):
        if not self.supressed:
            self.grid.controller.toggle_candidate(self.field.index,
                                                  self.index + 1)
            self.grid.bubble.update_btns()
            
    def activate(self):
        '''
        wrong candidates depression must be implemented here!!
        '''
        
        if self.grid.candidate_exist(self.field.index, self.index + 1):
            self.active = True
        else:
            self.active = False


class Undo_Btn(B_Btn):
    txt = UNDO_BTN_TXT
    
    def activate(self):
        self.active = False
        self.active = not self.grid.controller.history.i_am_at_bottom()

    def on_press(self):
        if self.active:
            self.grid.controller.undo()
            self.grid.bubble.update_btns()

class Redo_Btn(B_Btn):
    txt = REDO_BTN_TXT
    
    def activate(self):
        self.active = False
        self.active = not self.grid.controller.history.i_am_at_top()

    def on_press(self):
        if self.active:
            self.grid.controller.redo()
            self.grid.bubble.update_btns()

class Clr_Btn(B_Btn):
    txt = CLR_BTN_TXT
    
    def activate(self):
        self.active = not self.grid.field_is_empty(self.field)
        
    def on_press(self):
        if self.active:
            self.grid.controller.clear_field(self.field.index)
            self.grid.bubble.update_btns()
            
class Solve_Btn(B_Btn):
    txt = SOLVE_BTN_TXT
    
    def activate(self):
        self.active = not self.supressed
        
    def on_press(self):
        self.grid.controller.solve()
        self.grid.bubble.goodbye()
        
class Hint_Button(B_Btn):
    txt = HINT_BTN_TXT
    
    def activate(self):
        self.active = True
        
    def on_press(self):
        pass
        
class Show_Candidates_Btn(B_Btn):
    txt = SHOW_CAN_BTN_TXT
    
    def activate(self):
        self.active = not self.supressed
        
    def on_press(self):
        pass
 
class Input_Bubble(Bubble):

    def __init__(self, input_field, **kwargs):
        self.input_field = input_field
        self.grid = input_field.grid
        super(Input_Bubble, self).__init__(**kwargs)
         
        for i in range(self.grid.sdk_size):
            self.ids.value_block.add_widget(Val_Btn(input_field, i))
            self.ids.candidates_block.add_widget(Candidate_Btn(input_field, i))
        self.ids.func_block.add_widget(Clr_Btn(input_field))
        self.ids.func_block.add_widget(Undo_Btn(input_field))
        self.ids.func_block.add_widget(Redo_Btn(input_field))
        self.ids.func_block.add_widget(Solve_Btn(input_field))
        
        
    def update_btns(self):
        for block in self.ids.values():
            for btn in block.children:
                btn.activate()

    def goodbye(self):
        self.parent.remove_widget(self)
        self.input_field.clear_hl_col()
        self.grid.bubble = None
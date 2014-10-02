from kivy.lang import Builder

from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


import math
import numpy as np

NBLOCK_SCALE = 1.5
NBLOCK_FUNC_BTNS = 3

FIELD_SIZE = np.array([50, 50])
FIELD_SIZE_X = FIELD_SIZE.tolist()[0]
FIELD_SIZE_Y = FIELD_SIZE.tolist()[1]

UNDO_BTN_TXT = 'u'
REDO_BTN_TXT = 'r'
CLR_BTN_TXT = 'c'
MODE_BTN_TXT = '#'

BUBBLE_MODES = ['value', 'candidates']

EMPTY = 0

Builder.load_file('/home/flo/prj/sdk/sudoku.kv')


class Undo_Btn(BubbleButton):

    def __init__(self, grid, **kwargs):
        self.grid = grid
        super(Undo_Btn, self).__init__(**kwargs)
        self.text = UNDO_BTN_TXT
        self.active = not grid.history.i_am_at_bottom()

    def on_press(self):
        self.grid.set_data(self.grid.history.undo())


class Redo_Btn(BubbleButton):

    def __init__(self, grid, **kwargs):
        self.grid = grid
        super(Redo_Btn, self).__init__(**kwargs)
        self.text = REDO_BTN_TXT
        self.active = not grid.history.i_am_at_top()

    def on_press(self):
        self.grid.set_data(self.grid.history.redo())

class BubbleMode_Btn(BubbleButton):

    def __init__(self, bubble, **kwargs):
        self.bubble = bubble
        super(BubbleMode_Btn, self).__init__(**kwargs)
        self.text = MODE_BTN_TXT

    def on_press(self):
        self.bubble.toggle_mode()

class Clr_Btn(BubbleButton):

    def __init__(self, grid, **kwargs):
        self.grid = grid
        super(Clr_Btn, self).__init__(**kwargs)
        self.text = CLR_BTN_TXT
        self.active = not self.grid.active_field_is_empty()
        
    def on_press(self):
        self.grid.clear_active_field()


class Num_Btn(BubbleButton):

    value = EMPTY

    def __init__(self, grid, **kwargs):
        super(Num_Btn, self).__init__(**kwargs)
        self.grid = grid
        Num_Btn.value += 1
        self.value = Num_Btn.value
        self.text = str(self.value)

    def on_press(self):
        print('number button pressed')
        bubble = self.grid.bubble
        target_field = self.grid.active_field
        if bubble.mode == 'value':
            target_field.set_value(self.value)
            bubble.goodbye()
        elif bubble.mode == 'candidates':
            target_field.toggle_candidate(self.value)


class Input_Bubble(Bubble):

    def __init__(self, input_field, mode=0, **kwargs):
        super(Input_Bubble, self).__init__(**kwargs)
        self.input_field = input_field
        self.grid = input_field.parent
        self.mode = BUBBLE_MODES[mode]
        self.ncols = self.grid.box_size_x
        self.nrows = self.grid.box_size_y  + 1
        self.size = ((self.ncols, self.nrows) * FIELD_SIZE * 1.5).tolist()
        self.size_x = self.size[0]
        self.size_y = self.size[1]
        # calculate bubble position and set its "arrow_pos" property
        self.calc_bubble_pos()
        # add GridLayout for buttons
        self.buttons = GridLayout(cols=self.ncols)
        # create buttons
        self.add_widget(self.buttons)
        self.num_btns = [Num_Btn(self.grid) for _ in range(self.grid.sdk_size)]
        self.func_btns = {'clr': Clr_Btn(self.grid),
                          'mode': BubbleMode_Btn(self),
                          'undo': Undo_Btn(self.grid),
                          'redo': Redo_Btn(self.grid)}
        # add buttons
        for b in self.num_btns:
            self.buttons.add_widget(b)
        for b in self.func_btns.values():
            self.buttons.add_widget(b)
    
    def toggle_mode(self):
        print('toggle bubble mode')
        if self.mode == 'value':
            self.mode = 'candidates'
        elif self.mode == 'candidates':
            self.mode = 'value'
        print(self.mode)
        self.update_btn_col()
            
    def on_mode(self):
        print('mode changed:', self.mode)
        self.update_btn_col()
    
    def update_btn_col(self):
        # update number btns
        if self.mode == 'value':
            for b in self.num_btns:
                b.active = True
        elif self.mode == 'candidates':
            for i in range(len(self.num_btns)):
                self.num_btns[i].active = self.input_field.candidates[i]
        self.func_btns['undo'].active = not self.grid.history.i_am_at_bottom()
        print(self.func_btns['undo'].active)
        self.func_btns['redo'].active = not self.grid.history.i_am_at_top()
        self.func_btns['clr'].active = not self.grid.active_field_is_empty()
    
    def calc_bubble_pos(self):
        # calculate vertical and horizontal offset relative to grid center
        sdk_size = self.grid.sdk_size
        ix = self.input_field.ix
        iy = self.input_field.iy
        max_i = sdk_size - 1
        x_offs = ix - (max_i - ix)
        y_offs = iy - (max_i - iy)
        # create "arrow_pos" property for the bubble
        if x_offs > 0:
            horizontal_pos = 'right'
        else:
            horizontal_pos = 'left'
        if y_offs >= 0:
            vertical_pos = 'top'
        else:
            vertical_pos = 'bottom'
        if abs(x_offs) >= abs(y_offs):
            self.arrow_pos = horizontal_pos + '_' + vertical_pos
        else:
            self.arrow_pos = vertical_pos + '_' + horizontal_pos
        # get bubble position
        x = self.input_field.x
        y = self.input_field.y 
        options = {'top_left': lambda: (x, y - self.size_y),
                   'top_right': lambda: (x - (self.size_x - FIELD_SIZE_X),
                                         y - self.size_y),
                   'bottom_left': lambda: (x, y + FIELD_SIZE_Y),
                   'bottom_right': lambda: (x - (self.size_x - FIELD_SIZE_X),
                                            y + FIELD_SIZE_Y),
                   'left_top': lambda: (x + FIELD_SIZE_X,
                                        y - (self.size_y - FIELD_SIZE_Y)),
                   'left_bottom': lambda: (x + FIELD_SIZE_X,
                                         y),
                   'right_bottom': lambda: (x - self.size_x, y),
                   'right_top': lambda: (x - self.size_x,
                                         y - (self.size_y - FIELD_SIZE_Y))}
        self.pos = options[self.arrow_pos]()
               
    def goodbye(self):
        self.parent.remove_widget(self)
        self.grid.bubble = None
        self.grid.active_field = None
        Num_Btn.value = EMPTY
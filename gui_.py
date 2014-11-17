from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.vector import Vector
from kivy.graphics import Line, Color
from kivy.config import Config

import math
import collections

import sudoku
from input_bubble import Input_Bubble
import history



Builder.load_file('/home/flo/prj/sdk/sdk.kv')

NO_COLOR = (0, 0, 0, 0)

GRID_BKG_COL = (1, 1, 1, 1)

FIELD_BKG_COL_LOCKED = [.9, .8, .5, .2]
FIELD_BKG_COL_UNLOCKED = [0, 0, 0, 0]
FIELD_HL_COL_0 = [1, 1, 1, 0]
FIELD_HL_COL_1 = [.9, 0, .2, .4]
FIELD_TXT_COL_LOCKED = [0, 0, 0, 1]
FIELD_TXT_COL_UNLOCKED = [.1, 0, .3, 1]
FIELD_TXT_COL_WRONG = [1, 0, 0, 1]

CANDIDATE_TXT_COL_0 = (0, 0, 0, 1)
CANDIDATE_HL_COL_0 = (1, 1, 1, 0)
CANDIDATE_HL_COL_GN = (0, 1, 0, 1)
CANDIDATE_HL_COL_RD = (1, 0, 0, 1)

LINE_COL_MIN = (0, 0, 0, 1)
LINE_COL_MAJ = (0, 0, 0, 1)
LINE_WIDTH_MIN = 1.1
LINE_WIDTH_MAJ = 1.7

# sizes etc
FIELD_TXT_SCALE = 0.9
CANDIDATE_TXT_SCALE = 1

EMPTY = 0

class Field(FloatLayout):
    
    bkg_col = ListProperty(FIELD_BKG_COL_UNLOCKED)
    hl_col = ListProperty(NO_COLOR)
    txt_col = ListProperty(FIELD_TXT_COL_UNLOCKED)
    txt_scale = NumericProperty(FIELD_TXT_SCALE)
    text = StringProperty('')
    locked = False

    def __init__(self, grid, idx, **kwargs):
        self.grid = grid
        self.index = idx
        super(Field, self).__init__(**kwargs)
        
        if self.grid.values[self.index] != EMPTY:
            self.locked = True
            self.bkg_col = FIELD_BKG_COL_LOCKED
            self.txt_col = FIELD_TXT_COL_LOCKED
    
        self.cand_labels = [Candidate_Label() for __ in range(grid.sdk_size)]
        for c in self.cand_labels:
            self.ids.cnd_grid.add_widget(c)
        
        self.update_txt()
        self.update_candidates()

    def update_txt(self):
        val = self.grid.values[self.index]
        if val == EMPTY:
            self.text = ''
        else:
            self.text = str(val)
            
    def update_candidates(self):
        print('update candidates')
        cands = self.grid.candidates[self.index]
        for i, c in enumerate(self.cand_labels):
            if i in cands:
                c.text = str(i + 1)
            else:
                c.text = ''
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self.locked:
                self.grid.summon_bubble(field=self)
            return True
        return super(Field, self).on_touch_down(touch)
    
    def set_hl_col(self, col):
        self.hl_col = col
        
    def clear_hl_col(self):
        self.hl_col = NO_COLOR
        
    def i_am_empty(self):
        return self.grid.field_is_empty(self.index)

class Candidate_Grid(GridLayout):
    pass
 
class Candidate_Label(Label):
    hl_col = ListProperty(CANDIDATE_HL_COL_0)
    txt_col = ListProperty(CANDIDATE_TXT_COL_0)
    txt_scale = NumericProperty(CANDIDATE_TXT_SCALE)

class Grid(Widget):
    
    bkg_col = ListProperty(GRID_BKG_COL)
    values = ListProperty()
    candidates = ListProperty()
    bubble = None
       
    def __init__(self, sdk, **kwargs):
        print('init grid!!!')
        self.sdk_size = sdk.size
        super(Grid, self).__init__(**kwargs)
        
        self.sdk = sdk
        
        self.ids.grid.spacing = [2] * 2
        self.ids.grid.padding = [1] * 4

        self.init_options(show_candidates=False)
        
        self.bind(values=self.update,
                  candidates=self.update)
        self.values = sdk.get_data()['values']
        self.candidates = [[] for __ in range(sdk.size**2)]
        self.solution = sdk.solve()
        print(self.solution)
        
        self.history = history.History([self.get_data()])
        
        self.fields = [Field(self, i) for i in range(self.sdk_size**2)]
        
        for f in self.fields:
            self.ids.grid.add_widget(f)
                
        # draw lines
        self.collect_line_data()
        self.lines = []
        with self.canvas:    
            for data in self.line_data:
                Color(*data['col'], mode='rgba')
                self.lines.append(Line(points=data['points'],
                                       width=data['width']))
        self.bind(pos=self.update_lines, size=self.update_lines)

    def init_options(self, **kwargs):
        self.options = dict(
            show_candidates=False,
            show_wrong_values=False,
            supress_wrong_btns=False)
        for k, v in list(kwargs.items()):
            self.options[k] = v
            
    def on_values(self, instance, val):
        try:
            for f in self.fields:
                f.update_txt()
        except AttributeError:
            print('try to update values before fields are initiated!!')
            
    def on_candidates(self, instance, val):
        try:
            for f in self.fields:
                f.update_candidates()
        except AttributeError:
            print('try to update candidates before fields are initiated!!')
    
    def set_value(self, idx, val):
        self.values[idx] = val
        self.candidates[idx] = []
        self.push_to_history()
    
    def get_value(self, idx):
        return self.values[idx]
    
    def set_candidates(self, idx, array):
        self.candidates[idx] = array
        self.values[idx] = EMPTY
        self.push_to_history()
        
    def set_data(self, data, write_history=True):
        self.values = data['values']
        self.candidates = data['candidates']
        if write_history:
            self.push_to_history()

    def get_data(self):
        v = list(self.values)
        c = [list(f) for f in self.candidates]
        data = dict(values=v, candidates=c)
        return data
    
    def field_is_empty(self, idx):
        return self.values[idx] == EMPTY and not self.candidates[idx]
        
    def push_to_history(self):
        print('push grid to history')
        self.history.append(self.get_data())
        self.bubble.update_btns()
        print(self.history)
        
    def show_solution(self):
        self.values = self.solution
        self.candidates = [[] for __ in range(self.sdk_size**2)]
        self.push_to_history()
    
    def show_all_candidates(self):
        self.candidates = self.sdk.update_data(self.values)['candidates']
        self.push_to_history()
    
    def update(self, instance, val):
        opt = self.options
        
        if opt['show_candidates']:
            self.sdk.set_values(self.values)
            self.candidates = self.sdk.update_candidates()
        
        if self.bubble:
            self.bubble.update_btns()
  
    def summon_bubble(self, field):
        if self.bubble:
            if self.bubble.input_field == field:
                self.bubble.goodbye()
                return
            self.bubble.goodbye()
        field.set_hl_col(FIELD_HL_COL_1)
        self.bubble = Input_Bubble(input_field=field)
        self.add_widget(self.bubble)      
    
    def update_lines(self, instance, val):
        self.collect_line_data()
        for i, l in enumerate(self.lines):
            l.points = self.line_data[i]['points']            
    
    def collect_line_data(self):
        
        def walk_grid(a, b, step):
            while math.floor(a) <= b:
                yield math.floor(a)
                a += step
                
        step = Vector(self.size) / self.sdk_size
        step_x = step[0]
        step_y = step[1]
        x_min = self.pos[0]
        y_min = self.pos[1]
        x_max = x_min + self.size[0]
        y_max = y_min + self.size[1]
        self.line_data = []
        for i, x in enumerate(walk_grid(x_min, x_max, step_x)):
            if i % math.ceil(math.sqrt(self.sdk_size)) == 0:
                lcol = LINE_COL_MAJ
                lwidth = LINE_WIDTH_MAJ
            else:
                lcol = LINE_COL_MIN
                lwidth = LINE_WIDTH_MIN
            self.line_data.append({'points': (x, y_min, x, y_max),
                                   'col': lcol,
                                   'width': lwidth})
        for i, y in enumerate(walk_grid(y_min, y_max, step_y)):
            if i % math.ceil(math.sqrt(self.sdk_size)) == 0:
                lcol = LINE_COL_MAJ
                lwidth = LINE_WIDTH_MAJ
            else:
                lcol = LINE_COL_MIN
                lwidth = LINE_WIDTH_MIN
            self.line_data.append({'points': (x_min, y, x_max, y),
                                   'col': lcol,
                                   'width': lwidth})

class SDK_App(App):

    def build(self):
        sdk = sudoku.Sudoku9x9(data)
        root = Grid(sdk)
        return root


# example data
data = '400006007020090050003500600800000900030040060001000004005008200060050040900400008'

if __name__ == '__main__':
    Config.set('graphics', 'width', '500')
    Config.set('graphics', 'height', '500')
    SDK_App().run()
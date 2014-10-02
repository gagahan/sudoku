from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.label import Label

from kivy.uix.gridlayout  import GridLayout

from kivy.graphics import Color, Rectangle, Line
from kivy.vector import Vector

import numpy as np

Builder.load_file('/home/flo/prj/sdk/sudoku.kv')

FIELD_SIZE = np.array([50, 50])
FIELD_SIZE_X = FIELD_SIZE.tolist()[0]
FIELD_SIZE_Y = FIELD_SIZE.tolist()[1]

LINE_MAJ_COL = (.2, .2, .2, 1)
LINE_MAJ_WIDTH = 2.0
LINE_MIN_COL = (.3, .3, .3, 1)
LINE_MIN_WIDTH = 1.1

GRID_MARGIN_BOTTOM = 50
GRID_MARGIN_LEFT = 50
GRID_BOTTOM_LEFT_CORNER = (GRID_MARGIN_LEFT, GRID_MARGIN_BOTTOM)


EMPTY = 0


from sudoku import Sudoku9x9
from input_bubble import Input_Bubble
from grid_history import History

class Field(Label):
    
    index = 0
    
    def __init__(self, val, grid, **kwargs):
        self.locked = False if val == EMPTY else True
        super(Field, self).__init__(**kwargs)
        self.size = FIELD_SIZE.tolist()
        self.grid = grid
        self.index = Field.index
        Field.index += 1
        # add candidates to fields
        self.clear_candidates()
        # set field-text when value has changed
        self.bind(value=self.on_value)
        # set candidate text when a candidate has changed
        self.bind(candidates=self.on_candidates)
        # map text (actually show '' when '0')
        self.bind(text=self.map_text)
        # write value to field
        self.value = val
        
    def clear_candidates(self, data=[]):
        #print('clear candidates')
        self.candidates = [False] * self.grid.sdk_size
        for i in data:
            self.candidates[i] = True
        
    def clear(self):
        if not self.is_empty():
            self.clear_candidates()
            self.value = EMPTY
            self.grid.push_to_history()
            self.grid.bubble.update_btn_col()
    
    def toggle_candidate(self, i):
        print('toggle candidate: ', i)
        i -= 1
        self.candidates[i] = not self.candidates[i]
        self.grid.push_to_history()
        self.grid.bubble.update_btn_col()
    
    def set_value(self, val):
        if self.value != val:
            print('set value')
            self.value = val
            self.grid.push_to_history()
            self.grid.bubble.update_btn_col()
        
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if not self.locked:
                if touch.is_double_tap:
                    bubble_mode = 1
                else:
                    bubble_mode = 0
                self.grid.summon_bubble(field=self, mode=bubble_mode)
            return True
        return super(Field, self).on_touch_down(touch)
        
    def map_text(self, instance, val):
        if self.text == str(EMPTY):
            self.text = ''
                
    def on_value(self, instance, val):
        #print('value changed!')
        # clear candidates
        if self.value != EMPTY:
            self.clear_candidates()
        # set field text
        self.text = str(self.value)
        
    def on_candidates(self, instance, val):
        #print('candidate changed!')
        # clear value
        if not self.candidates_are_empty():
            self.value = EMPTY
        # set text for candidate labels
        for i in range(self.grid.sdk_size):
            if self.candidates[i]:
                s = str(i + 1)
            else:
                s = ''
            self.candidate_field.children[-i - 1].text = s
    
    def candidates_are_empty(self):
        return all(EMPTY == c for c in self.candidates)
    
    def is_empty(self):
        return self.candidates_are_empty() and not self.value


class Candidate_Label(Label):
    pass

class Candidate_field(GridLayout):
    
    def __init__(self, field, **kwargs):
        self.pos = field.pos
        self.size = field.size
        super(Candidate_field, self).__init__(**kwargs)
        self.cols = 3
        for _ in range(field.grid.sdk_size):
            self.add_widget(Candidate_Label(text=''))


class Grid(Widget):
    
    def __init__(self, sdk, **kwargs):
        super(Grid, self).__init__(**kwargs)
        self.sdk = sdk
        self.sdk_size = size = sdk.size
        self.size = (FIELD_SIZE * size).tolist()
        self.box_size = sdk.get_box_size().tolist()
        self.box_size_x = self.box_size[0]
        self.box_size_y = self.box_size[1]
        self.active_field = None
        self.bubble = None
        # create_fields
        self.fields = [Field(v, self) for v in sdk.get_values()]
        # push data to grid history
        self.history = History()
        self.push_to_history()
        # add position info to each field
        grid_pos = [(x, y) for y in reversed(range(size)) for x in range(size)]
        for i in range(len(self.fields)):
            # position grid index (0..size-1)
            self.fields[i].ix = grid_pos[i][0]
            self.fields[i].iy = grid_pos[i][1]
        # add display position to each field
        for f in self.fields:
            x = f.ix * FIELD_SIZE_X + GRID_MARGIN_LEFT
            y = f.iy * FIELD_SIZE_Y + GRID_MARGIN_BOTTOM
            f.pos = (x, y)
        # create candidate fields
        self.candidate_fields = [Candidate_field(f) for f in self.fields]
        # link fields and candidate fields
        for i in range(len(self.fields)):
            self.fields[i].candidate_field = self.candidate_fields[i]
        # add candidate fields to grid
        for c in self.candidate_fields:
            self.add_widget(c)        
        # add fields to grid
        for f in self.fields:
            self.add_widget(f)
        # draw grid lines
        self.draw_lines()
        self.show_all_candidates()

    def summon_bubble(self, field, mode):
        print('summon bubble, mode:', mode)
        if self.bubble:
            if self.active_field == field:
                if not(self.bubble.mode == 'value' 
                       and mode == 'candidates'):
                    self.bubble.goodbye()
                    return
            self.bubble.goodbye()
        self.active_field = field
        self.bubble = Input_Bubble(input_field=field, mode=mode)
        # add bubble to grid
        self.add_widget(self.bubble)

    def push_to_history(self):
        print('push data to history')
        # collect data
        d = {}
        d['values'] = [f.value for f in self.fields]
        d['candidates'] = [list(f.candidates) for f in self.fields]
        # add data to history
        self.history.append(d)
        print(self.history)
        
    # overwrite all values and candidates
    # (dict with 'values' and 'candidates' keys expected)
    def set_data(self, data):
        try:
            for i in range(len(self.fields)):
                self.fields[i].value = data['values'][i]
                self.fields[i].candidates = data['candidates'][i]
                self.bubble.update_btn_col()
            print(self.history)
        except KeyError:
            print('grid.get_data: data incompatible!')
            
    def active_field_is_empty(self):
        f = self.active_field
        if f:
            return f.is_empty()
        else:
            return True
            
    def clear_active_field(self):
        f = self.active_field
        if f:
            f.clear()
    
    
    def show_all_candidates(self):
        candidates = self.sdk.update_candidates()
        print('..',candidates)
        for idx, f in enumerate(self.fields):
            f.clear_candidates(candidates[idx])
        self.push_to_history()
            
    def draw_lines(self):
        box_size_x = int(self.box_size[0])
        box_size_y = int(self.box_size[1])
        max_x = (self.sdk_size + 1) * FIELD_SIZE[0]
        max_y = (self.sdk_size + 1) * FIELD_SIZE[1]
        with self.canvas:
            # minor lines first
            w = LINE_MIN_WIDTH
            c = LINE_MIN_COL
            Color(c[0], c[1], c[2], c[3], mode='rgba')
            # draw horizontal lines_y
            for x in range(FIELD_SIZE[0], max_x + FIELD_SIZE[0], FIELD_SIZE[0]):
                Line(points=[x, max_y, x, FIELD_SIZE[1]], width=w)
            # draw vertical lines
            for y in range(FIELD_SIZE[1], max_y + FIELD_SIZE[1], FIELD_SIZE[1]):  
                Line(points=[max_x, y, FIELD_SIZE[0], y], width=w)
            # major (box) lines on top
            w = LINE_MAJ_WIDTH
            c = LINE_MAJ_COL
            Color(c[0], c[1], c[2], c[3], mode='rgba')
            # draw horizontal lines_y
            for x in range(FIELD_SIZE[0], max_x + FIELD_SIZE[1], FIELD_SIZE[1] * box_size_x):
                Line(points=[x, max_y, x, FIELD_SIZE[1]], width=w)
            # draw vertical lines
            for y in range(FIELD_SIZE[1], max_y + FIELD_SIZE[1], FIELD_SIZE[1] * box_size_y):  
                Line(points=[max_x, y, FIELD_SIZE[0], y], width=w)
        
        
data1 = '400006007020090050003500600800000900030040060001000004005008200060050040900400008'
data2 = '459326187126897453783514692874631925532749861691285374345978216268153749917462538'
data3 = '459000180126897453783514690004631925532749861691280000045978216268153749917462530'

class MyApp(App):

    title = 'gagahan'

    def build(self):
        sdk = Sudoku9x9(data1)
        root = Widget()
        root.add_widget(Grid(sdk, pos=GRID_BOTTOM_LEFT_CORNER))
        return root

    
if __name__ == '__main__':
    MyApp().run()

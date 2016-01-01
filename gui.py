import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.widget import Widget 
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import (ListProperty, NumericProperty, StringProperty,
                             DictProperty, BooleanProperty, ObjectProperty) 
from kivy.vector import Vector
from kivy.graphics import Line, Color
from kivy.config import Config
from kivy.uix.progressbar import ProgressBar


import math

import sudoku
from input_bubble import Input_Bubble
from controller import Controller


Builder.load_file('/home/flo/prj/sdk/sdk.kv')

NO_COLOR = (0, 0, 0, 0)

GRID_BKG_COL = (1, 1, 1, 1)

FIELD_BKG_COL_LOCKED = [.9, .8, .5, .1]
FIELD_BKG_COL_UNLOCKED = [0, 0, 0, 0]
FIELD_HL_COL_0 = [0, .9, .2, .1]
FIELD_HL_COL_1 = [.2, 0, .9, .1]
FIELD_HL_COLS = (FIELD_HL_COL_0,
                 FIELD_HL_COL_1)
FIELD_TXT_COL_LOCKED = [0, 0, 0, 1]
FIELD_TXT_COL_UNLOCKED = [.1, 0, .3, 1]
FIELD_TXT_COL_WRONG = [1, 0, 0, 1]

CANDIDATE_TXT_COL_0 = (0, 0, 0, 1)
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
    
        self.cand_labels = [Candidate_Label() for __ in range(grid.sdk_size)]
        for c in self.cand_labels:
            self.ids.cnd_grid.add_widget(c)
        
        self.update_values([])
        self.update_candidates([])


    def update_values(self, values):
        for candidate in values:
            if candidate['field'] == self.index:
                self.text = str(candidate['val'])
                break
        else:
            self.text = ''
         
            
    def update_candidates(self, candidates):
        cands = [c['val'] for c in candidates
                 if c['field'] == self.index]
        for i, c in enumerate(self.cand_labels):
            if i + 1 in cands:
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


class Candidate_Grid(GridLayout):
    pass

 
class Candidate_Label(Label):
    
    hl_col = ListProperty(NO_COLOR)
    txt_col = ListProperty(CANDIDATE_TXT_COL_0)
    txt_scale = NumericProperty(CANDIDATE_TXT_SCALE)


class GridView(Widget):
    
    
    bkg_col = ListProperty(GRID_BKG_COL)
    values = ListProperty()
    candidates = ListProperty()
    bubble = None
    show_hint = BooleanProperty(False)
    active_hint = ObjectProperty(None)
    hints = ListProperty()   
       
    def __init__(self, presenter, **kwargs):
        self.sdk_size = sdk_size = presenter.get_sdk_size()
        self.controller = presenter
        super(GridView, self).__init__(**kwargs)
        
        x = math.ceil(math.sqrt(sdk_size))
        y = sdk_size // x
        self.box_size = [x, y]
        
        self.ids.grid.spacing = [2] * 2
        self.ids.grid.padding = [1] * 4
        
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
            
    
    def register(self, presenter):
        presenter.add_view(self)
        
            
    def on_values(self, instance, val):
        vals = self.sdk_to_ui(self.values)
        try:
            for f in self.fields:
                f.update_values(vals)
        except AttributeError:
            print('try to update values before fields are initiated!!')
            
            
    def on_candidates(self, instance, val):
        cands = self.sdk_to_ui(self.candidates)
        try:
            for f in self.fields:
                f.update_candidates(cands)
        except AttributeError:
            print('try to update candidates before fields are initiated!!')
  
            
    def on_show_hint(self, instance, val):
        if self.show_hint:
            self.show_me_the_hint(self.active_hint)
        else:
            self.clr_hl()
       
    
    def on_active_hint(self, instance, val):
        if self.active_hint and self.show_hint:
            self.show_me_the_hint(self.active_hint)
        
    def field_is_empty(self, field):
        return not (field.index in self.values or 
                    field.index in self.candidates)
        
        
    def candidate_exist(self, field_idx, val):
        c = field_idx * self.sdk_size + (val - 1)
        if (c in self.candidates):
            return True
        else:
            return False
  
    
    def show_me_the_hint(self, hint):
        self.clr_hl()
        # highlight house
        for i, house in enumerate(hint.houses):
            for idx in house:
                col_idx = i % len(FIELD_HL_COLS)
                self.fields[idx].set_hl_col(FIELD_HL_COLS[col_idx])
        # mark members
        for candidate in self.sdk_to_ui(hint.members):
            idx = candidate['field']
            val = candidate['val']
            self.fields[idx].cand_labels[val - 1].hl_col = CANDIDATE_HL_COL_GN
        # mark obsoletes
        for candidate in self.sdk_to_ui(hint.obsoletes):
            idx = candidate['field']
            val = candidate['val']
            self.fields[idx].cand_labels[val - 1].hl_col = CANDIDATE_HL_COL_RD

    
    def clr_hl(self):
        # clr all highlighting
        for f in self.fields:
            f.set_hl_col(NO_COLOR)
            for c in f.cand_labels:
                c.hl_col = NO_COLOR
  
  
    def summon_bubble(self, field):
        if self.bubble:
            if self.bubble.input_field == field:
                self.bubble.goodbye()
                return
            self.bubble.goodbye()
        field.set_hl_col(FIELD_HL_COL_1)
        self.bubble = Input_Bubble(input_field=field)
        self.add_widget(self.bubble)     
        
        
    def update(self, data):
        self.values = data['values']
        self.candidates = data['candidates']
        self.hints = data['hints']
        self.show_hint = data['show_hint']
        self.active_hint = data['active_hint']
        print(self.active_hint)
        
        
    def sdk_to_ui(self, sdk_candidates):
        ui_candidates = [{'field': c // self.sdk_size,
                          'val': c % self.sdk_size + 1
                          }
                         for c in sdk_candidates]
        return ui_candidates
        
    def lock_fields(self):
        for candidate in self.values:
            idx = candidate // self.sdk_size
            self.fields[idx].locked = True
            self.fields[idx].txt_col = FIELD_TXT_COL_LOCKED
            self.fields[idx].bkg_col = FIELD_BKG_COL_LOCKED
                
                
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


class ProgressView(ProgressBar):
    
    offset = 0
    
    def register(self, presenter):
        presenter.add_view(self)
    
    def update(self, data):
        self.value = len(data['values']) - self.offset



class NextHintBtn(Button):

    def on_press(self):
        self.parent.presenter.next_hint()
        
    
class PrevHintBtn(Button):
    
    def on_press(self):
        self.parent.presenter.prev_hint()

class ApplyHintBtn(Button):
    
    def on_press(self):
        self.parent.presenter.gui_data['active_hint'].apply()
    
    
class ShowHintBtn(Button):
    
    def on_press(self):
        self.parent.presenter.gui_data['show_hint'] ^= True
        self.parent.presenter.update_views()


class MenuButtonsView(BoxLayout):
    
    
    def __init__(self, **kwargs):
        super(MenuButtonsView, self).__init__(**kwargs)
        self.padding = 10
        self.add_widget(PrevHintBtn(text='prev'))
        self.add_widget(ApplyHintBtn(text='apply'))
        self.add_widget(ShowHintBtn(text='show/hide'))
        self.add_widget(NextHintBtn(text='next'))
        
    
    def register(self, presenter):
        presenter.add_view(self)
        self.presenter = presenter
        
        
    def update(self, data):
        pass
    

class SDK_App(App):


    def build(self): 
        sdk = sudoku.Sudoku9x9(xw1) 
        #sdk.print_dlx(file='/home/flo/prj/sdk/dlx_data/lc1.txt')
        ctrl = Controller(sdk=sdk)
        
        
        grid = GridView(ctrl, pos=(0,100), size=(500, 500))
        grid.register(ctrl)
        
        prog_bar = ProgressView(max=ctrl.n_unknown_fields,
                                 pos=(0, 0), size=(500, 50))
        prog_bar.offset = ctrl.n_given_fields
        prog_bar.register(ctrl)
        
        hint_menu = MenuButtonsView(cols=4, pos=(0, 50), size=(500, 50))
        hint_menu.register(ctrl)
        
        ctrl.update_views()
        
        grid.lock_fields()
        
        
        root = FloatLayout(size_hint=(0, 0))
        root.add_widget(grid)
        root.add_widget(prog_bar)
        root.add_widget(hint_menu)
        
        return root


# example data
data1 = '400006007020090050003500600800000900030040060001000004005008200060050040900400008'
data2 = '000005080000601043000000000010500000000106000300000005530000061000000004000000000'
ns1 = '412736589 000000106 568010370 000850210 100000008 087090000 030070865 800000000 000908401'
lc1 = '318005406 000603810 006080503 864952137 123476958 795318264 030500780 000007305 000039641'
lc2 = '340006070 080000930 002030060 000010000 097364850 000002000 000000000 000608090 000923785'
np1 = '700849030 928135006 400267089 642783951 397451628 815692300 204516093 100008060 500004010'
np2 = '687004523 953002614 142356978 310007246 760000305 020000701 096001032 230000057 070000069'
np3 = '050134600 090652138 030879040 215003006 080261350 360085921 040027013 073006000 020308760'
nt1 = '000294380 000178640 480356100 004837501 000415700 500629834 953782416 126543978 040961253'
nt2 = '390000700 000000650 507000349 049380506 601054983 853000400 900800134 002940865 400000297'
nt3 = '400500370 320000004 060000000 800002030 210840000 000000090 070090100 940651000 000070000'
nq1 = '010720563 056030247 732546189 693287415 247615938 581394000 000002000 000000001 005870000'
hp1 = '049132000 081479000 327685914 096051800 075028000 038046005 853267000 712894563 964513000'
hp2 = '000060000 000042736 006730040 094000068 000096407 607050923 100000085 060080271 005010094'
ht1 = '280000473 534827196 071034080 300500040 000340060 460790310 090203654 003009821 000080937'
ht2 = '500620037 004890000 000050000 930000000 020000605 700000003 000009000 000000700 680570002'
hq1 = '816573294 392000000 457209006 941000568 785496123 623800040 279000001 138000070 564000082'
hq2 = '030000010 008090000 400608000 000576940 000983520 000124000 276005190 000709000 095000470'
xw1 = '041729030 769003402 032640719 403900170 607004903 195370024 214567398 376090541 958431267'

if __name__ == '__main__':
    Config.set('graphics', 'width', '500')
    Config.set('graphics', 'height', '600')
    SDK_App().run()
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget


from sudoku import Sudoku9x9
from grid import Grid


Builder.load_file('/home/flo/prj/sdk/sudoku.kv')


data1 = '400006007020090050003500600800000900030040060001000004005008200060050040900400008'
ns1 = '412736589 000000106 568010370 000850210 100000008 087090000 030070865 800000000 000908401'
lc1 = '318005406 000603810 006080503 864952137 123476958 795318264 030500780 000007305 000039641'
lc2 = '340006070 080000930 002030060 000010000 097364850 000002000 000000000 000608090 000923785'

class SudokuApp(App):

    title = 'gagahan'

    def build(self):
        sdk = Sudoku9x9(lc2)
        root = Widget()
        grid = Grid(sdk, pos=(50,50))
        root.add_widget(grid)
        sdk.update_human_techniques()
        return root

    
if __name__ == '__main__':
    SudokuApp().run()
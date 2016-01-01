import math
import numpy as np

from dlx import SDK_DLX
from constraint import CellConstraint
from constraint import RowConstraint
from constraint import ColConstraint
from constraint import BoxConstraint


class Sudoku:


    size = 0
    EMPTY_CELL = -1
    values = set()
    candidates = set()
    

    def __init__(self, data):
        self.set_values(data)
        self.n_locked_fields = len(self.values)
        self.update_candidates()
        self.update_hints()
        self.solution = self.solve()

            
    def solve(self):
        m = SDK_DLX(self.size, self.constraints, self.values) 
        solution = m.search(limit=1)[0]
        return solution

    
    def is_unique(self):
        m = SDK_DLX(self.size, self.constraints, self.values) 
        m.search(2)
        if len(m.solution) > 1:
            return False
        else:
            return True

    
    # calculate field number from dlx candidate
    def field_num(self, y):
        return y // self.size

    
    # calculate value from dlx candidate
    def val(self, y):
        return y % self.size

    
    def update_candidates(self):
        m = SDK_DLX(self.size, self.constraints, self.values)
        self.candidates = m.get_candidates()


    def update_hints(self):
        m = SDK_DLX(self.size, self.constraints, self.values)
        self.hints = ([h for h in m.search_naked_singles()] +
                      [h for h in m.search_hidden_singles()] +
                      [h for h in m.search_locked_candidates()] +
                      [h for h in m.search_naked_subset(2)] +
                      [h for h in m.search_naked_subset(3)] +
                      [h for h in m.search_naked_subset(4)] +
                      [h for h in m.search_hidden_subset(2)] +
                      [h for h in m.search_hidden_subset(3)] +
                      [h for h in m.search_hidden_subset(4)] +
                      [h for h in m.search_fish(2)]
                      )

    def set_values(self, data):
        if data:
            try:
                vls = [int(v) - 1 for v in list(data) if v.isnumeric()]
            except AttributeError:
                vls = [v -1 for v in data]
            if len(vls) != self.size**2:
                print('error while importing values: length invalid!')
                raise Exception
            else:
                self.values = {i * self.size + v for i, v in enumerate(vls) 
                               if vls[i] != self.EMPTY_CELL}
    
            
    def get_ncols(self):
        return (math.ceil(math.sqrt(self.size)))
    
        
    def get_box_size(self):
        x = math.ceil(math.sqrt(self.size))
        y = self.size // x
        return np.array([x, y])
        
        
    def show(self):
        s = self.__repr__()
        print('\n'.join([s[i:i + self.size] for i in range(0, len(s), self.size)]))
    
    
    def __repr__(self):
        return ''.join(map(str, self.get(mapper='+1')))
    
    def print_dlx(self, file='sys.stdout'):
        m = SDK_DLX(self.size, self.constraints, self.values) 
        if file != 'sys.stdout':
            f = open(file, 'w')
        else:
            f = file    
        print(m, file=f)
  
  
class Sudoku9x9(Sudoku):


    def __init__(self, data=''):
        self.size = size = 9
        self.constraints = [CellConstraint(size), 
                            RowConstraint(size),
                            ColConstraint(size),
                            BoxConstraint(size)]
        for i, const in enumerate(self.constraints):
            const.set_offset(i)
        dlx_cols = self.size**2 * len(self.constraints)
        dlx_rows = self.size**3
        self.dlx_size = (dlx_cols, dlx_rows)
        #self.box_size = self.get_box_size()
        Sudoku.__init__(self, data)
        


if __name__ == '__main__':
    data1 = '400006007020090050003500600800000900030040060001000004005008200060050040900400008'

    const = CellConstraint()
    for i in range(9**2):
        house = const.get_house(i)
        print(i, house)
import math
import os
import numpy as np

from dlx import SDK_DLX


class Constraint:
    def __init__(self, size=9):
        self.size = size
        self.size_sqr = self.size**2
        
    def get_y(self, y, n):
        return self.func(y) + self.get_offset(n)
        
    def get_offset(self, n):
        return self.size_sqr * n
    
    def func(self, y):
        raise NotImplementedError('function must be defined')

class Row_Col_Constraint(Constraint):
    # row-column constraint (row + column)
    def func(self, y):
        return y // self.size

class Val_Row_Constraint(Constraint):
    # value-row constraint (row + val * size)
    def func(self, y):
        return y // self.size_sqr + (y % self.size) * self.size

class Val_Col_Constraint(Constraint):
    # value-column constraint (col + val * size)
    def func(self, y):
        return y // self.size % self.size + (y % self.size) * self.size

class Val_Box_Constraint(Constraint):
    def __init__(self, size=9):
        Constraint.__init__(self, size=9)
        self.box_size = int(math.sqrt(size))
    # value-box constraint (box + val * size)
    def func(self, y):
        return ((y // self.size % self.size) // self.box_size
                + y // self.size_sqr // self.box_size * self.box_size
                + (y % self.size) * self.size)       
    

class Sudoku:

    size = 0
    EMPTY_CELL = -1
    
    def solve(self):
        m = SDK_DLX(self.size, self.dlx_size, self.constraints, self.values) 
        m.search(1)
        if m.solution:
            self.data.set(self.dlx_to_sdk(m.solution[0]))
            return True
        else:
            return False
    
    def is_unique(self):
        m = SDK_DLX(self.size, self.dlx_size, self.constraints, self.values) 
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
        m = SDK_DLX(self.size, self.dlx_size, self.constraints, self.values)
        self.candidates = m.get_candidates()
        return self.get_candidates()

    def set_values(self, data):
        self.values = []
        try:
            vls = [int(v) - 1 for v in list(data) if v.isnumeric()]
            if len(vls) != self.size**2:
                print('error while importing values: length invalid!')
                raise Exception
            else:
                self.values = [i * self.size + v for i, v in enumerate(vls) 
                               if vls[i] != self.EMPTY_CELL]
        except Exception:
            print('error while importing values')
    
    def get_values(self):
        values = [self.EMPTY_CELL] * self.size**2
        for y in self.values:
            values[self.field_num(y)] = self.val(y)
        values = [v + 1 for v in values]
        return values
    
    def get_candidates(self):
        candidates = [[] for __ in range(self.size**2)]
        for y in self.candidates:
            candidates[self.field_num(y)].append(self.val(y))
        return candidates
    
    def get_data(self):
        return dict(zip(['values', 'candidates'], [self.get_values(), self.get_candidates()]))
        
    def get_box_size(self):
        x = math.ceil(math.sqrt(self.size))
        y = self.size // x
        return np.array([x, y])
    
    def update_human_techniques(self):
        m = SDK_DLX(self.size, self.dlx_size, self.constraints, self.values)
        ns = m.naked_singles()
        hs = m.hidden_singles()
        lc = m.locked_candidates()
        print('naked singles:')
        for c in ns:
            print('cell:', self.field_num(c.y), ', val :', self.val(c.y))
        print('hidden singles:')
        for c in hs:
            print('cell:', self.field_num(c.y), ', val :', self.val(c.y))
        print('locked candidates:')
        for c in lc:
            print('cell:', self.field_num(c.y), ', val :', self.val(c.y))
        
        
    def show(self):
        s = self.__repr__()
        print('\n'.join([s[i:i + self.size] for i in range(0, len(s), self.size)]))
    
    def __repr__(self):
        return ''.join(map(str, self.get(mapper='+1')))
    
  
class Sudoku9x9(Sudoku):

    def __init__(self, data=''):
        self.size = size = 9
        self.constraints = []
        self.constraints.append(Row_Col_Constraint(size).get_y)
        self.constraints.append(Val_Row_Constraint(size).get_y)
        self.constraints.append(Val_Col_Constraint(size).get_y)
        self.constraints.append(Val_Box_Constraint(size).get_y)
        dlx_cols = self.size**2 * len(self.constraints)
        dlx_rows = self.size**3
        self.dlx_size = (dlx_cols, dlx_rows)
        #self.box_size = self.get_box_size()
        self.set_values(data)
        self.update_candidates()
        
 
if __name__ == '__main__':
    data1 = '400006007020090050003500600800000900030040060001000004005008200060050040900400008'

    sdk = Sudoku9x9(data1)
    print(sdk.get_candidates())
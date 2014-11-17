import math
import os
import numpy as np
import hint

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
    values = set()
    candidates = set()


    def __init__(self, data):
        self.update_data(data)
        self.solution = self.solve()

            
    def solve(self):
        m = SDK_DLX(self.size, self.dlx_size, self.constraints, self.values) 
        solution = m.search(limit=1)[0]
        return solution

    
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

    
    def update_data(self, values=None):
        if values:
            self.set_values(values)
        m = SDK_DLX(self.size, self.dlx_size, self.constraints, self.values)
        self.candidates = m.get_candidates()


    def set_values(self, data):
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
    
    
    def naked_singles(self):
        m = SDK_DLX(self.size, self.dlx_size, self.constraints, self.values)
        for data in m.naked_singles():
            yield data
            
        
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
        Sudoku.__init__(self, data)
        


if __name__ == '__main__':
    data1 = '400006007020090050003500600800000900030040060001000004005008200060050040900400008'

    sdk = Sudoku9x9()
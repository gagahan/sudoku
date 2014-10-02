import math
        
class Node:
    def __init__(self, col = -1, row = -1, ntype = 'r'):
        self.y = row
        self.x = col
        self.ntype = ntype

class Walk_Matrix:
    walk = {'right': lambda n: n.right,
            'left' : lambda n: n.left,
            'up' : lambda n: n.up,
            'down' : lambda n: n.down}
    
    def __init__(self, n, direction='right', end=False):
        self.stop = n
        self.step = n
        self.direction = direction
        self.end_condition = end

    def __iter__(self):
        return(self)

    def __next__(self):
        self.step = self.walk[self.direction](self.step)
        if self.step == self.stop or self.end_condition:
            raise StopIteration
        return self.step
        
        
class DLX():
    def __init__(self, dlx_size=(0,0), constraints=[], candidates=()):
        self.tmp_solution = []
        self.solution = []
        self.constraints = constraints
        self.n_cols = dlx_size[0]
        self.n_rows = dlx_size[1]
        self.create_empty_matrix()
        self.put_to_solution(*candidates)
        self.solution_count = 0
        
    def link_horizontal(self, array):
            for i in range(len(array)):
                array[i].left = array[i - 1]
                array[i - 1].right = array[i]

    def link_vertical(self, array):
            for i in range(len(array)):
                array[i].up = array[i -1]
                array[i - 1].down = array[i]
                array[i].col = array[0]
                
    def create_empty_matrix(self):
        # set up matrix, init header nodes (+1 root node at the end)
        self.matrix = [[Node(x, 0, 'h')] for x in range(self.n_cols + 1)]
        # link header nodes horizontaly
        self.link_horizontal([col[0] for col in self.matrix])
        # create pointer to root node
        self.root_node = self.matrix[-1][0]
        # set up row buffer
        row_buffer = [None] * len(self.constraints)
        for y in range(self.n_rows):
            for n in range(len(self.constraints)):
                x = self.constraints[n](y, n)
                row_buffer[n] = Node(x, y)
                self.matrix[x].append(row_buffer[n])
            # create horizontal links
            self.link_horizontal(row_buffer)
        # in every column..
        for col in self.matrix:
            # ..create vertical links, add column pointers
            self.link_vertical(col)
            # ..add colum size to each header node
            col[0].col_size = len(col) - 1

    def cover(self, c):
        c.left.right = c.right
        c.right.left = c.left
        for i in Walk_Matrix(c, direction='down'):
            print
            for j in Walk_Matrix(i, direction='right'):
                j.up.down = j.down
                j.down.up = j.up
                j.col.col_size -= 1

    def uncover(self, c):
        for i in Walk_Matrix(c, direction='up'):
            for j in Walk_Matrix(i, direction='left'):
                j.down.up = j
                j.up.down = j
                j.col.col_size += 1
        c.right.left = c
        c.left.right = c    
        
    def search(self, limit=1):
        # a solution is found when all columns are covered
        if self.root_node.right == self.root_node:
            self.solution_count += 1
            self.solution.append([n.y for n in self.tmp_solution])
            return
        # choose column with fewest candidates
        header = [c for c in Walk_Matrix(self.root_node, direction='right')]
        c = sorted(header, key=lambda x: x.col_size)[0]
        self.cover(c)
        # try every candidate in column
        for r in Walk_Matrix(c, direction='down'):
            self.tmp_solution.append(r)
            for j in Walk_Matrix(r, direction='right'):
                self.cover(j.col)
            if self.solution_count < limit:
                self.search(limit)
            # backtracking
            r = self.tmp_solution.pop()
            for j in Walk_Matrix(r, direction='left'):
                self.uncover(j.col)
        self.uncover(c)

    def put_to_solution(self, *candidates):
        if candidates:
            for y in candidates:
                # get x for first constraint
                x = self.constraints[0](y, 0)
                # search row
                r = self.matrix[x][1]
                while r.y != y: r = r.down
                self.tmp_solution.append(r)
                self.cover(r.col)
                for j in Walk_Matrix(r, direction='right'):
                    self.cover(j.col)
                    
    def __repr__(self):
        ncol = range(len(self.matrix))
        nrow = range(self.size**3)
        m = [['  ' for _ in nrow] for _ in ncol]
        for c in Walk_Matrix(self.root_node, direction='right'):
            for r in Walk_Matrix(c, direction='down'):
                m[r.x][r.y] = str(r.y)
        s = ''
        for y in nrow:
            for x in ncol:
                s += m[x][y]
            s += '\n'
        return s
    
    
class SDK_DLX(DLX):
    
    def __init__(self, size, dlx_size=(0,0), constraints=[], candidates=()):
        DLX.__init__(self, dlx_size, constraints, candidates)
        self.size = size
        self.size_sqr = size**2
    
    def get_candidates(self):
        candidates = []
        for c in Walk_Matrix(self.root_node, direction='right'):
            if c.x >= self.size_sqr: break
            candidates += [r.y for r in Walk_Matrix(c, direction='down')]
        return candidates
    
    # walk constraint(s)
    def constraint(self, *const):
        for i in const:
            # goto first node
            l_const = self.size_sqr
            n = self.root_node
            i_am_in = lambda c: n.x >= c * l_const and n.x < (c + 1) * l_const
            while not i_am_in(i):
                n = n.right 
                if n == self.root_node:
                    print('constraint is empty!!')
                    raise Exception
            # walk constraint
            while i_am_in(i):
                yield n
                n = n.right
                
    # search naked singles
    def naked_singles(self):
        output = []
        for c in self.constraint(0):
            if c.col_size == 1:
                output.append(c.down)
        return output
    
    # search hidden singles    
    def hidden_singles(self):
        output = []
        for c in self.constraint(1,2,3):
            if c.col_size == 1:
                output.append(c.down)
        return output
    
    # search locked candidates
    def locked_candidates(self):
        output = []
        # search for all types of locked candidates
        d = {'row-box': (1, lambda x: x.right.right, 'row-box'),
             'col-box': (2, lambda x: x.right, 'col-box'),
             'box-row': (3, lambda x: x.left.left, 'box-row'),
             'box-col': (3, lambda x: x.left, 'box-col')}
        # !! what about x-sudoku constraints???!!!!!
        for entry in d.values():
            # walk constraint
            for c in self.constraint(entry[0]):
                if c.col_size > 1:
                    tmp = [entry[1](n) for n in Walk_Matrix(c, 'down')]
                    # if all array b.x are the same?
                    if all(n.x == tmp[0].x for n in tmp):
                        # walk array b[0].col
                        for n in Walk_Matrix(tmp[0].col, 'down'): 
                            # if n not in array
                            if not n in tmp:
                                # its a locked candidate
                                #print(entry[2], ':', n.y//9, ',',n.y%9)
                                output.append(n)
        return output
    

        

if __name__ == '__main__':
    pass

import itertools
import hint
import constraint

        
class Node:
    
    def __init__(self, col=-1, row=-1, sdk_size=9):
        self.y = row
        self.x = col
        self.sdk_size = sdk_size
        
    
    def get_val(self):
        return self.y % self.sdk_size
    


class HeaderNode(Node):
    
    const = None
    
    def get_const(self):
        return self.const
    
    
    def get_house(self):
        return self.const.get_house()
    
    
        
class Walk_Matrix:
    walk = {'right': lambda n: n.right,
            'left' : lambda n: n.left,
            'up' : lambda n: n.up,
            'down' : lambda n: n.down}
    
    def __init__(self, n, direction='right'):
        self.stop = n
        self.step = n
        self.direction = direction

    def __iter__(self):
        return(self)

    def __next__(self):
        self.step = self.walk[self.direction](self.step)
        if self.step == self.stop:
            raise StopIteration
        return self.step
        
        
class SDK_DLX():
    def __init__(self, size=9, constraints={}, candidates=()):
        self.size = size
        self.size_sqr = size ** 2
        self.tmp_solution = []
        self.solution = []
        self.constraints = constraints
        self.n_constraints = len(constraints)
        self.constraint_table = {c.name: c for c in self.constraints}
        self.n_cols = self.size_sqr * len(constraints)
        self.n_rows = self.size ** 3
        self.create_empty_matrix()
        self.put_to_solution(*candidates)
        self.solution_count = 0

        
        
    def link_horizontal(self, array):
            for i in range(len(array)):
                array[i].left = array[i - 1]
                array[i - 1].right = array[i]


    def link_vertical(self, array):
            for i in range(len(array)):
                array[i].up = array[i - 1]
                array[i - 1].down = array[i]
                array[i].col = array[0]
                
                
    def create_empty_matrix(self):
        # set up matrix, init header nodes (+1 root node at the end)
        self.matrix = [[HeaderNode(x, 0, self.size)] 
                       for x in range(self.n_cols + 1)]
        # link header nodes horizontally
        self.link_horizontal([col[0] for col in self.matrix])
        # create pointer to root node
        self.root_node = self.matrix[-1][0]
        self.root_node.const = constraint.Constraint()
        # set up row buffer
        row_buffer = [None] * len(self.constraints)
        # for all rows in sparse matrix
        for y in range(self.n_rows):
            # fill buffer with one node per constraint 
            for i, const in enumerate(self.constraints):
                x = const.get_x(y)
                row_buffer[i] = Node(x, y)
                self.matrix[x].append(row_buffer[i])
                # add constraint name and number to column header
                # (will be written several times during initialization)
                self.matrix[x][0].const = const
                self.matrix[x][0].const_i = const.get_const_number(x)
                self.matrix[x][0].n_const = i
            # create horizontal links for the row
            self.link_horizontal(row_buffer)
        # in every column..
        for col in self.matrix:
            # ..create vertical links, add column pointers
            self.link_vertical(col)
            # ..add column size to each header node
            col[0].col_size = len(col) - 1


    def cover(self, c):
        c.left.right = c.right
        c.right.left = c.left
        for i in Walk_Matrix(c, direction='down'):
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
            self.solution.append({n.y for n in self.tmp_solution})
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
        return self.solution


    def put_to_solution(self, *candidates):
        if candidates:
            for y in candidates:
                # get x for first constraint
                x = self.constraint_table['cell'].get_x(y)
                # search row
                r = self.root_node.right
                for row in Walk_Matrix(self.root_node, direction='right'):
                    if row.x > x:
                        raise Exception('column already covered!!')
                    if row.x == x:
                        for r in Walk_Matrix(row, direction='down'):
                            if r.y > y:
                                raise Exception('node already covered!!')
                            if r.y == y:
                                self.tmp_solution.append(r)
                                self.cover(r.col)
                                for j in Walk_Matrix(r, direction='right'):
                                    self.cover(j.col)
                                break
                        break
                    
                    
    def __repr__(self):
        print('fucked up since constraints are stored in a dict')
        '''
        # header works only for sdk 9x9
        size = 9
        s = ('\t' + 'r\t' * size**2 + 'v\t' * size**2 * 3 + '\n' +
             '\t' + '\t'.join([str(i // size % size) for i in range(size**2 * 4)]) + '\n' +
             '\t' + 'c\t' * size**2 + 'r\t' * size**2 + 'c\t' * size**2 + 'b\t' * size**2 + '\n' +
             '\t' + '\t'.join([str(i % size) for i in range(size**2 * 4)]) + '\n'
             )
        m = [['\t' for _ in range(self.n_rows)] for _ in range(self.n_cols)]
        for c in Walk_Matrix(self.root_node, direction='right'):
            for r in Walk_Matrix(c, direction='down'):
                m[r.x][r.y] = str(1) + '\t'
        for y in range(self.n_rows):
            s += ('r' + str(y // size**2 % size) +
                  'c' + str(y // size % size) +
                  'v' + str(y % size) + '\t'
                  )
            for x in range(self.n_cols):
                s += m[x][y]
            s += '\n'
        return s
    '''
    
    def get_candidates(self):
        cands = set()
        for c in Walk_Matrix(self.root_node, direction='right'):
            if c.x >= self.size_sqr: break
            cands = cands | {r.y for r in Walk_Matrix(c, direction='down')}
        return cands

    
    # walk constraint(s)
    def walk_constraint(self, *constraints, start=None):
        for name in constraints:
            # goto first node
            if start:
                x = start.col
            else:
                x = self.root_node
            while x.const.name != name:
                x = x.right 
                if x == self.root_node:
                    raise Exception('constraint is empty!!')
            # walk constraint
            while x.const.name == name:
                yield x
                x = x.right

                
    # walk col(s)
    def walk_col(self, *cols):
        for col in cols:
            y = col.down
            while y.ntype != 'h':
                yield  y
                y = y.down

                
    def walk_set_of_cols(self, cols): 
        for col in cols:
            y = col.down
            while y.ntype != 'h':
                yield  y
                y = y.down


    def get_house(self, c):
        const_name = c.col.const.name
        while c.col.const.name != 'cell':
            c = c.left
        x = c.x - self.constraint_table['cell'].offset
        return self.constraint_table[const_name].get_house(x)

    def get_neighbor(self, node, const_name):
        while node.col.const.name != const_name:
            node = node.right
        return node 

    # search naked singles
    def search_naked_singles(self):
        for c in self.walk_constraint('cell'):
            if c.col_size == 1:
                members = [c.down.y]
                house = self.get_house(c.down)
                yield hint.NakedSingle(members=members, houses=[house])
        
        
    # search hidden singles    
    def search_hidden_singles(self):
        for const_name in self.constraint_table:
            if const_name == 'cell':
                continue
            for c in self.walk_constraint(const_name):
                if c.col_size == 1:
                    members = [c.down.y]
                    house = house = self.get_house(c.down)
                    yield hint.HiddenSingle(members=members, houses=[house])

    
    # search locked candidates
    # assumed, there's a "box-constraint"
    def search_locked_candidates(self):
        
        # create map
        tmp_list = tuple(s for s in self.constraint_table 
                         if (s != 'cell' and s != 'box'))
        c_map = {s: ('box', ) for s in tmp_list}
        c_map['box'] = tmp_list      
        
        for const_a in c_map:
            # walk constraint
            for c in self.walk_constraint(const_a):
                if c.col_size <= 1:
                    continue
                members = []
                obsoletes = []
                for const_b in c_map[const_a]:
                    tmp = [self.get_neighbor(n, const_b)
                           for n in Walk_Matrix(c, 'down')]
                    # if all x are the same?
                    if all(n.x == tmp[0].x for n in tmp):
                        # walk array b[0].col
                        for n in Walk_Matrix(tmp[0].col, 'down'): 
                            # if n not in array
                            if not n in tmp:
                                # its a locked candidate
                                members += [t.y for t in tmp]
                                obsoletes.append(n.y)
                                house2 = self.get_house(c.down)
                                house1 = self.get_house(n)
                        if obsoletes:
                            yield hint.LockedCandidate(obsoletes=obsoletes,
                                                       members=members,
                                                       houses=[house1, house2])
    
    
    def get_all_houses(self, min_cands=1):
        houses = {k: tuple(set() for __ in range(self.size))
                  for k in self.constraint_table}
        for h in self.walk_constraint('cell'):
            if h.col_size >= min_cands:
                for cand in Walk_Matrix(h, 'down'):
                    for c in Walk_Matrix(cand, 'right'):
                        houses[c.col.const.name][c.col.const_i].add(h)
        return houses
        
    
    
    def search_naked_subset_new(self, n):
        members = []
        for cell in self.walk_constraint('cell'):
            if cell.col_size > n or cell.col_size < 2:
                continue
            for cand in Walk_Matrix(cell, 'down'):
                members.append(cand)
                
                for const in Walk_Matrix(cand, 'right'):
                    for c in Walk_Matrix(const, 'down'):
                        m = self.get_neighbor(c, 'cell')
                        if m.col.col_size < 2:
                            continue
                        
                        
                        
        
    def search_naked_subset(self, n):

        # get all houses
        houses = self.get_all_houses(min_cands=2)
        for const in houses:
            for house in houses[const]:
                # try all subset combinations
                for subs in itertools.combinations(house, n):
                    # collect values
                    subs_cands = [list(Walk_Matrix(h, 'down')) for h in subs]
                    subs_cands = set(itertools.chain(*subs_cands))
                    values = {cand.get_val() for cand in subs_cands}
                    # how many different values in subset?
                    if len(values) != n:
                        continue
                    # collect obsoletes
                    house_cands = [list(Walk_Matrix(h, 'down')) for h in house]
                    house_cands = set(itertools.chain(*house_cands))
                    diff_cands = house_cands - subs_cands
                    obsoletes = [c.y for c in diff_cands 
                                 if c.get_val() in values]
                    # if some obsolete candidates are found, its a naked subset
                    if obsoletes:
                        hint_house = self.constraint_table[const].\
                                                get_house(subs[0].x)
                        yield hint.NakedSubset(obsoletes=obsoletes,
                            members=[c.y for c in subs_cands],
                            houses=[hint_house])
                    

    # search hidden subsets
    def search_hidden_subset(self, n):
        
        # get all houses
        houses = self.get_all_houses()
        for const in houses:
            for house in houses[const]:
                # collect candidates form house
                house_cands = [list(Walk_Matrix(h, 'down')) for h in house]
                house_cands = set(itertools.chain(*house_cands))
                for subs in itertools.combinations(house, n):                  
                    if {h.x for h in subs} == {42, 43}:
                        pass
                    # collect candidates from subset
                    subs_cands = [list(Walk_Matrix(h, 'down')) for h in subs]
                    subs_cands = set(itertools.chain(*subs_cands))
                    subs_values = {n.get_val() for n in subs_cands}
                    # collect candidate values from the cells
                    # who doesn't belonging to subset
                    other_values = {n.get_val() 
                                    for n in house_cands - subs_cands}
                    # collect candidate values who exist only in subset
                    v_exclusive_in_subset = subs_values - other_values 
                    # count them
                    if len(v_exclusive_in_subset) == n:
                        # subset found
                        # search for obsoletes
                        obsoletes = [n.y for n in subs_cands 
                                if n.get_val() not in v_exclusive_in_subset]
                        if obsoletes:
                            # push members to output
                            members = [n.y for n in subs_cands
                                       if n.get_val() in v_exclusive_in_subset]
                            # get house
                            h = self.constraint_table[const].\
                                                get_house(subs[0].x)
                            yield hint.HiddenSubset(obsoletes=obsoletes,
                                                    members=members,
                                                    houses=[h])
                            
                            
    def search_fish(self,n=2):                        
        pass
        # basic fish : row - col, col - row
        # franken fish: row/box - col/box, col/box - row/box
        # mutant fish: row/col/box - row/col/box
        
        # take n base-sets
        # oberlap?
        #    -> endo fins?
        
        # find n cover-sets
        # overlap?
        #    -> cannibalism?
        # cover all base candidates?
        #    -> 
        #
        

        get_values = lambda h: {cand.get_val() for cell in h 
                                        for cand in Walk_Matrix(cell, 'down')}
                
        # get all houses
        houses = self.get_all_houses()
        houses_flat =[]
        for const in houses:
            for house in houses[const]:
                houses_flat.append(dict(const=const, cells=house))
        
        # choose base-sets
        for base_set in tuple(itertools.combinations(houses_flat, n)):
            
            # choose value
            # the value must occur in every house from the base-set
            bs_values = set.intersection(*[get_values(house['cells']) 
                                           for house in base_set])
            if base_set[0]['const'] == 'row' and base_set[1]['const'] == 'row':
                pass
            
            # check overlapping
            pass
        
        yield hint.Fish()
                
        
        
    
    def print_cand(self, y):
        cell = y // 9
        val = y % 9
        print('c', cell, ', v', val)
    
   

if __name__ == '__main__':
    pass

import gui_

DIFF_NAKED_SINGLE = 1

HOUSE_HL_COL_1 = (.5, .5, .1, .3)

CANDIDATES_HL_COL_RD = (1, 0, 0, 1)
CANDIDATES_HL_COL_GN = (0, 1, 0, 1)

ROW_COL_CONSTRAINT = 0

class Solution_Step:

    '''
    candidates = [{'col': None,
                   'field': None,
                   'candidates': []}]
    '''
    
    def __init__(self, dlx):
        self.dlx = dlx
        self.root_node = dlx.root_node
        self.sdk_size = dlx.size
        
    def search(self, dlx):
        raise NotImplementedError('function must be defined')
    
        # walk constraint(s)
    def walk_constraint(self, *const, start=None):
        for n in const:
            # goto first node
            if start:
                x = start
            else:
                x = self.root_node
            while x.const_num != n:
                x = x.right 
                if x == self.root_node:
                    print('constraint is empty!!')
                    raise Exception
            # walk constraint
            while x.const_num == n:
                yield x
                x = x.right
                
    def get_val(self, node):
        return node.y % self.sdk_size

class Naked_Single(Solution_Step):
    
    difficulty = DIFF_NAKED_SINGLE
    
    def search(self):
        output = []
        for c in self.walk_constraint(ROW_COL_CONSTRAINT):
            if c.col_size == 1:
                field_number = c.x
                hl_cand = self.get_val(c.down)
                house = dict(col=HOUSE_HL_COL_1, fields=[c.x])
                candidate = dict(col=CANDIDATES_HL_COL_GN,
                                  field=field_number,
                                  candidate=hl_cand)
                step = dict(name='Naked Single',
                            diff=self.difficulty,
                            houses=[house], 
                            candidates=[candidate])
                output.append(step)
        return output

       
    
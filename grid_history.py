class History(list):

    def __init__(self, *args):
        list.__init__(self, *args)
        self.idx = len(self) - 1

    def append(self, d):
        print('new data', d)
        # delete everything after index
        del(self[self.idx + 1:])
        # check for max length limit
        pass
        # add data to list
        super(History, self).append(d)
        # increment index
        self.idx += 1
        
    def undo(self):
        print('undo')
        if self:
            if self.idx > 0:
                self.idx -= 1
            return self[self.idx]
    
    def redo(self):
        print('redo')
        if self:
            if self.idx < len(self) - 1:
                self.idx += 1
            return self[self.idx]
    
    def i_am_at_bottom(self):
        return self.idx <= 0
    
    def i_am_at_top(self):
        return self.idx == len(self) - 1
    
    def __repr__(self):
        s = 'history:\n' + str(len(self)) + ' steps stored\n'\
        + 'idx: ' + str(self.idx) + '\n'\
        + 'at_bottom: ' + str(self.i_am_at_bottom()) + ' '\
        + ', at_top: ' + str(self.i_am_at_top())
        return s
        
def show(l):
    for d in l:
        print(d)
    
if __name__ == '__main__':
    l = History()
    d = {'a': [0, 1], 'b': [[False, False], [False, False]]}
    l.append(d)
    show(l)
    d = {'a': [2, 3], 'b': [[False, False], [True, False]]}
    l.append(d)
    show(l)
    l.append(2)
    print(l[0])
    
class History(list):

    def __init__(self, limit=100, *args):
        list.__init__(self, *args)
        self.idx = len(self) - 1

    def append(self, d):
        # delete everything after index
        del(self[self.idx + 1:])
        # check for max depth limit
        pass
        # add data to list
        super(History, self).append(d)
        # increment index
        self.idx += 1
    
    def undo(self):
        if self:
            self.idx -= 1
            return self[self.idx]
    
    def redo(self):
        if self:
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
        + ', at_top: ' + str(self.i_am_at_top()) + '\n'\
        + (str(self[self.idx]) if self else str([]))
        return s
    
if __name__ == '__main__':
    h = History(['a', 'b', 'c'])
    print(h, h.idx)
    h.append('d')
    print(h, h.idx)
    print(h.undo())
    print(h, h.idx)
    h.append('e')
    print(h, h.idx)
    print(h.undo())
    print(h, h.idx)
    print(h.redo())
    print(h, h.idx)
    for d in h:
        print(d)
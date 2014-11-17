class Hint:
    '''
    a object of this class must contain the following info
    - candidates where the technique is applied on
    - candidates who can be deleted when the technique will be applied
    - cells from one or more house(s) who belongs to the technique
    - a method for applying the technique 
    '''

    members = []
    obsoletes = []
    house = []
    
    difficulty = -1
    effeciency = 0
            
            
    def __init__(self, **kwargs):
        if 'members' in kwargs:
            self.members = kwargs['members']
        if 'obsoletes' in kwargs:
            self.obsoletes = kwargs['obsoletes']
        if 'house' in kwargs:
            self.house = kwargs['house']
            
        
    def apply(self):
        raise NotImplementedError('function must be defined')


    
class NakedSingle(Hint):
    
    def __init__(self, **kwargs):
        Hint.__init__(self, kwargs)
        self.name = 'Naked Single'
        self.difficulty = 0
        self.effeciency = 100
        
    def apply(self):
        pass
        
            
if __name__ == '__main__':
    test = Hint()
    print(test.active_candidates)
    print(test.obsolete_candidates)
class Hint():
    '''
    a object of this class must contain the following info
    - candidates where the technique is applied on ("members")
    - candidates who can be deleted when the technique will be applied
      ("obsoletes")
    - cells from one or more house(s) who belongs to the technique ("houses")
    - a method for applying the technique 

    "members" and "obsoletes" are stored as a list of sdk.
    "houses" are stored as a list of list containing field_indexes.
    '''
    
    members = []
    obsoletes = []
    houses = []
    
    difficulty = -1
    effeciency = 0
    
    def __init__(self, **kwargs):
        if 'members' in kwargs:
            self.members = kwargs['members']
        if 'obsoletes' in kwargs:
            self.obsoletes = kwargs['obsoletes']
        if 'houses' in kwargs:
            self.houses = kwargs['houses']
        
    def apply(self):
        raise NotImplementedError('function must be defined')


class NakedSingle(Hint):

    name = 'Naked Single'
    difficulty = 0.1
    effeciency = 100
        
        
    def apply(self, ctrl):
        candidate = self.members[0]
        ctrl.set_value(candidate['field'], candidate['val'])
        
        
class HiddenSingle(NakedSingle):

    name = 'Hidden Single'
    difficulty = 0.2
    effeciency = 100
    
    
class LockedCandidate(Hint):
    
    name = 'Locked Candidate'
    difficulty = 0.3
    effeciency = 50
    

class NakedSubset(Hint):
    
    name = 'Naked Subset'
    difficulty = 0.4
    effeciency = 50
    

class HiddenSubset(Hint):
    
    name = 'Hidden Subset'
    difficulty = 0.5
    effeciency = 50   
    

class Fish(Hint):
    
    name = 'fish'
    difficulty = 1
    effeciency = 50  



if __name__ == '__main__':
    pass
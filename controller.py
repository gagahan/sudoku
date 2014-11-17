import history

class Controller:
    
    views = []
    options = {'manual_candidates': True}
    
    def __init__(self, **kwargs):
        
        self.sdk = kwargs['sdk']
        try:
            self.views.append = kwargs['ui']
        except KeyError:
            pass
        
        self.history = history.History()
        self.push_data_to_history()
        
 
    def add_view(self, ui):
        self.views.append(ui)
        
    def get_sdk_size(self):
        return self.sdk.size

    def  set_value(self, field_idx, val):
        # manipulate sdk data
        for old_val in self.sdk.values:
            if self.field_num(old_val) == field_idx:
                self.sdk.values.remove(old_val)
                break
        new_val = self.ui_to_sdk(field_idx, val)    
        self.sdk.values.add(new_val)
        self.sdk.update_data()
        #self.clear_candidates(field_idx)
        
        
        # push to history
        self.push_data_to_history()
    
        # update view
        self.update_views()


    def toggle_candidate(self, field_idx, val):
        # manipulate sdk data
        self.clear_value(field_idx)
        candidate = self.ui_to_sdk(field_idx, val)
        if candidate in self.sdk.candidates:
            self.sdk.candidates.remove(candidate)
        else:
            self.sdk.candidates.add(candidate)

        # push to history
        self.push_data_to_history()
        
        # update view
        self.update_views()
        
        
    def solve(self):
        self.sdk.values = self.sdk.solution
        self.sdk.candidates.clear()
        
        self.push_data_to_history()
                
        self.update_views()
        
        
    def clear_field(self, field_idx):
        # manipulate sdk data
        self.clear_value(field_idx)   
        self.sdk.update_data()     
        #self.clear_candidates(field_idx)

        # push to history
        self.push_data_to_history()
        
        # update view
        self.update_views()
        
        
    def clear_value(self, field_idx):
        for val in self.sdk.values:
            if self.field_num(val) == field_idx:
                self.sdk.values.remove(val)
                break
            
        
    def clear_candidates(self, field_idx):
        candidates = [c for c in self.sdk.candidates
                      if self.field_num(c) == field_idx]
        for c in candidates:
            self.sdk.candidates.remove(c)
        
        
    def push_data_to_history(self):
        h_data = dict(values=set(self.sdk.values),
                      candidates=set(self.sdk.candidates))
        self.history.append(h_data)
        
        
    def undo(self):
        h_data = self.history.undo()
        self.sdk.values = set(h_data['values'])
        self.sdk.candidates = set(h_data['candidates'])
        
        self.update_views()
        
        
    def redo(self):
        h_data = self.history.redo()
        self.sdk.values = set(h_data['values'])
        self.sdk.candidates = set(h_data['candidates'])
        
        self.update_views()        
        
        
    def get_all_hints(self):
        pass
    
    def update_views(self):
        # collect data and convert to view format        
        values = self.sdk_to_ui(self.sdk.values)
        candidates = self.sdk_to_ui(self.sdk.candidates)
        data = dict(values=values,
                    candidates=candidates)
        
        # update views
        # every view must update must provide a update method
        for view in self.views:
            view.update(data)
            
            
    def field_num(self, y):
        return y // self.sdk.size
    
    def val(self, y):
        return y % self.sdk.size + 1
    
    def sdk_to_ui(self, sdk_candidates):
        d = {self.field_num(c): [] for c in sdk_candidates}
        for c in sdk_candidates:
            d[self.field_num(c)].append(self.val(c))
        return d
        
    def ui_to_sdk(self, field_idx, val):
        return field_idx * self.sdk.size + (val - 1)
        
import history
import hint
        

class Controller:
    
    views = []
    gui_data = dict(show_hint=False, active_hint=None)
    
    def __init__(self, **kwargs):
        
        self.sdk = kwargs['sdk']
        
        try:
            self.views.append = kwargs['ui']
        except KeyError:
            pass
        
        self.n_given_fields = len(self.sdk.values)
        self.n_unknown_fields = self.sdk.size**2 - self.n_given_fields
        
        self.history = history.History()
        self.push_data_to_history()
        
        self.reset_active_hint()
        
 
    def add_view(self, *ui):
        for view in ui:
            self.views.append(view)
        
        
    def get_sdk_size(self):
        return self.sdk.size


    def  set_value(self, field_idx, val):
        # manipulate sdk data
        self.clear_value(field_idx)
        new_val = self.ui_to_sdk(field_idx, val)    
        self.sdk.values.add(new_val)
        self.sdk.update_candidates()
        self.sdk.update_hints()
        self.reset_active_hint()
        
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
            
        self.sdk.update_hints()
        self.reset_active_hint()
        
        # push to history
        self.push_data_to_history()
        
        # update view
        self.update_views()
        
        
    def solve(self):
        self.sdk.values = self.sdk.solution
        self.sdk.candidates.clear()
        
        self.sdk.update_hints()
        self.reset_active_hint()
        
        self.push_data_to_history()
        
        self.update_views()
        
        
    def clear_field(self, field_idx):
        # manipulate sdk data
        self.clear_value(field_idx)
        self.sdk.update_candidates()     
        
        #if not auto_candidate_mode:
        #self.clear_candidates(field_idx)
        
        self.sdk.update_hints()
        self.reset_active_hint()

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
        
    
    def reset_active_hint(self):
        if self.sdk.hints:
            self.gui_data['active_hint'] = self.sdk.hints[0]
        else:
            self.gui_data['active_hint'] = None
        
    def next_hint(self):
        if self.sdk.hints:
            hints = self.sdk.hints
            act_h = self.gui_data['active_hint']
            i = (hints.index(act_h) + 1) % len(hints)
            self.gui_data['active_hint'] = hints[i]
            self.update_views()
        

    def prev_hint(self):
        if self.sdk.hints:
            hints = self.sdk.hints
            act_h = self.gui_data['active_hint']
            i = hints.index(act_h) -1
            self.gui_data['active_hint'] = hints[i]
            self.update_views()

        
    def push_data_to_history(self):
        h_data = dict(values=set(self.sdk.values),
                      candidates=set(self.sdk.candidates))
        self.history.append(h_data)
        
        
    def undo(self):
        h_data = self.history.undo()
        self.sdk.values = set(h_data['values'])
        self.sdk.candidates = set(h_data['candidates'])
        
        self.sdk.update_hints()
        self.reset_active_hint()
        
        self.update_views()
        
        
    def redo(self):
        h_data = self.history.redo()
        self.sdk.values = set(h_data['values'])
        self.sdk.candidates = set(h_data['candidates'])
        
        self.sdk.update_hints()
        self.reset_active_hint()
        
        self.update_views()        
        
            
    def update_views(self):        
        values = self.sdk.values
        candidates = self.sdk.candidates
        hints = self.sdk.hints
        for h in hints:
            print(h.name, h.members, h.obsoletes, h.houses)
        
        data = dict(values=values,
                    candidates=candidates,
                    hints=hints,
                    show_hint=self.gui_data['show_hint'],
                    active_hint=self.gui_data['active_hint']
                    )
                    
        # update views
        # every view must update must provide a update method
        for view in self.views:
            view.update(data)
            
            
    def field_num(self, y):
        return y // self.sdk.size
    
    
    def val(self, y):
        return y % self.sdk.size + 1
    

        
        
    def ui_to_sdk(self, field_idx, val):
        return field_idx * self.sdk.size + (val - 1)
        
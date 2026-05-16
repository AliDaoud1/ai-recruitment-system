class SessionManager:
    def __init__(self):
        self.selected_file = None

    def select(self, file):
        self.selected_file = file

    def clear(self):
        self.selected_file = None

    def is_selected(self):
        return self.selected_file is not None
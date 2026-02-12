class Context:
    def __init__(self):
        self.last_seen_rowid = 0

    def update_last_seen(self, rowid):
        self.last_seen_rowid = rowid

# Global context instance
context = Context()

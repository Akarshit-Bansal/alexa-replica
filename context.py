class ContextMemory:
    def __init__(self):
        self.context = {}

    def set_context(self, key, value):
        self.context[key] = value

    def get_context(self, key):
        return self.context.get(key)

    def clear_context(self):
        self.context = {}

    def update_context(self, intent, entities):
        # Update based on intent
        if intent == 'weather':
            self.set_context('last_query', 'weather')
        # Add more logic as needed

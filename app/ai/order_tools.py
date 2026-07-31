from django.contrib.sessions.backends.base import SessionBase


class ConversationMemory:

    SESSION_KEY = "smart_ai_memory"

    def __init__(self, request):
        self.request = request
        self.session: SessionBase = request.session

    def load(self):
        return self.session.get(self.SESSION_KEY, [])

    def save(self, history):
        self.session[self.SESSION_KEY] = history
        self.session.modified = True

    def clear(self):
        self.session.pop(self.SESSION_KEY, None)

    def add(self, role, content):

        history = self.load()

        history.append({

            "role": role,

            "content": content

        })

        history = history[-20:]

        self.save(history)
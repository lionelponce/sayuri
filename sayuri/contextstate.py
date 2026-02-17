import json
from datetime import datetime, timezone

class ContextState:
    def __init__(self, conversation_id: str = 'syr000'):
        self.conversation_id = conversation_id
        self.project = None
        self.topic = None
        self.goals = []
        self.assumptions = []
        self.decisions = []
        self.flags = {}
        self.last_updated = datetime.now(timezone.utc)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.last_updated = datetime.now(timezone.utc)

    def to_json(self):
        return json.dumps(self.__dict__, default=str, indent=2)

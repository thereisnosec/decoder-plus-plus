from core.plugin.abstract_plugin import AbstractPlugin
from core.command import Command

class Plugin(AbstractPlugin):

    def __init__(self, context):
        # Name, Type, Author, Dependencies
        super().__init__('MD5', Command.Type.HASHER, "Thomas Engel", ["hashlib"])

    def run(self, text):
        import hashlib
        return hashlib.md5(text.encode('utf-8')).hexdigest()

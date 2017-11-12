from enum import Enum


class NodeType(Enum):
    NEW_LINE = 1
    TEXT = 2


class BaseNode:
    type = None

    def __repr__(self):
        return '<%s(%s)>' % (
            self.__class__.__name__,
            self.__dict__,
        )


class NewLineNode(BaseNode):
    type = NodeType.NEW_LINE


class TextNode(BaseNode):
    type = NodeType.TEXT

    def __init__(self, text):
        self.text = text

import abc
import sys
from dataclasses import dataclass
from typing import Dict, Union


def _camel(snake_str):
    "from https://stackoverflow.com/questions/19053707/converting-snake-case-to-lower-camel-case-lowercamelcase"
    words = snake_str.lower().split('_')
    return ''.join([*map(str.title, words)])


def factory(web_template_node, *args, **kwargs):
    dv_stripped = web_template_node.rm_type.replace('DV_', '', 1)
    class_name = _camel(dv_stripped)
    try:
        return getattr(sys.modules[__name__], class_name)(*args, **kwargs)
    except TypeError as ex:
        raise FactoryWrongArguments(
            f'failed building {class_name}, {web_template_node.path}. Given args: {args},\
            kwargs {kwargs}') from ex


class FactoryWrongArguments(Exception):
    pass


class DataValue(abc.ABC):
    @abc.abstractmethod
    def to_json(self) -> Union[Dict, str]:
        ...


@dataclass
class Text(DataValue):
    value: str

    def to_json(self) -> str:
        return self.value


@dataclass
class DateTime(Text):
    ...


@dataclass
class Date(Text):
    ...


@dataclass
class Duration(Text):
    ...


@dataclass
class Boolean(Text):
    ...


@dataclass
class CodePhrase(DataValue):
    terminology: str
    code: str
    preferred_term: str = None

    def to_json(self) -> Dict:
        dct = {'code': self.code, 'terminology': self.terminology}
        if self.preferred_term:
            dct['preferred_term'] = self.preferred_term
        return dct


class CodedText(DataValue):
    def __init__(self, value, terminology, code, preferred_term=None):
        self.value = value
        self._code_phrase = CodePhrase(terminology, code, preferred_term)

    @property
    def terminology(self):
        return self._code_phrase.terminology

    @property
    def code(self):
        return self._code_phrase.code

    @property
    def preferred_term(self):
        return self._code_phrase.preferred_term

    def to_json(self) -> Dict:
        dct = self._code_phrase.to_json()
        dct['value'] = self.value
        return dct


@dataclass
class Identifier(DataValue):
    id_: str
    issuer: str = None
    assigner: str = None
    type_: str = None

    def to_json(self) -> Dict:
        dct = {'id': self.id_}
        for attr in ('issuer', 'assigner', 'type_'):
            value = getattr(self, attr)
            if value is not None:
                dct[attr.strip('_')] = value
        return dct


@dataclass
class PartyProxy(DataValue):
    # TODO: check if it is the right representation
    name: str

    def to_json(self):
        return {'name': self.name}

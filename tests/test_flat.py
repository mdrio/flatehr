#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

import openehr_client.data_types as data_types
from openehr_client.flat import Composition, CompositionNode, WebTemplateNode


def test_web_template_node(web_template_json):
    WebTemplateNode.create(web_template_json)


@pytest.mark.skip("Composition.get TBD")
def test_composition_get_path(web_template_json):
    web_template = WebTemplateNode.create(web_template_json)
    composition = Composition(web_template)
    text = 'ok'
    path = '/test/context/status'
    composition.set(path, text)
    node = composition.get(path)
    assert isinstance(node.value, data_types.Text)


def test_composition_set_path_dv_text(web_template_json):
    web_template = WebTemplateNode.create(web_template_json)
    composition = Composition(web_template)
    text = 'ok'
    path = 'test/context/status'
    node = composition.set(path, text)
    assert isinstance(node, CompositionNode)
    assert isinstance(node.value, data_types.Text)
    assert node.value.value == text

    flat = composition.as_flat()
    assert flat == {path: text}


def test_composition_set_path_code_phrase(web_template_json):
    web_template = WebTemplateNode.create(web_template_json)
    composition = Composition(web_template)
    terminology = 'ISO_639-1'
    code = 'en'
    path = 'test/language'

    node = composition.set(path, terminology=terminology, code=code)
    assert isinstance(node.value, data_types.CodePhrase)
    assert node.value.terminology == terminology
    assert node.value.code == code

    flat = composition.as_flat()
    assert flat == {f'{path}|code': code, f'{path}|terminology': terminology}


def test_composition_set_path_dv_coded_text(web_template_json):
    web_template = WebTemplateNode.create(web_template_json)
    composition = Composition(web_template)
    text = 'ok'
    terminology = 'ISO_639-1'
    code = 'en'
    path = 'test/context/setting'
    node = composition.set(path, text, terminology=terminology, code=code)
    assert isinstance(node.value, data_types.CodedText)

    assert node.value.value == text
    assert node.value.terminology == terminology
    assert node.value.code == code

    flat = composition.as_flat()
    assert flat == {
        f'{path}|code': code,
        f'{path}|terminology': terminology,
        f'{path}|value': text
    }


def test_composition_set_path_dv_datetime(web_template_json):
    web_template = WebTemplateNode.create(web_template_json)
    composition = Composition(web_template)
    text = '2021-04-22T10:19:49.915Z'
    path = 'test/context/start_time'
    node = composition.set(path, text)
    assert isinstance(node.value, data_types.DateTime)
    assert node.value.value == text

    flat = composition.as_flat()
    assert flat == {path: text}


def test_composition_set_path_party_proxy(web_template_json):
    web_template = WebTemplateNode.create(web_template_json)
    composition = Composition(web_template)
    name = 'composer'
    path = 'test/composer'
    node = composition.set(path, name)
    assert isinstance(node.value, data_types.PartyProxy)
    assert node.value.name == name

    flat = composition.as_flat()
    assert flat == {f'{path}|name': name}


def test_composition_to_flat(web_template_json):
    web_template = WebTemplateNode.create(web_template_json)
    composition = Composition(web_template)
    composition = Composition(web_template)
    text = 'ok'
    path_status = 'test/context/status'
    composition.set(path_status, text)

    terminology = 'ISO_639-1'
    code = 'en'
    path_lang = 'test/language'

    composition.set(path_lang, terminology=terminology, code=code)

    flat = composition.as_flat()
    assert flat == {
        path_status: text,
        f'{path_lang}|code': code,
        f'{path_lang}|terminology': terminology
    }

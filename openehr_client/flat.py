import re
from typing import Dict, Tuple, Union

import anytree


class Node:
    def __init__(self, node: anytree.Node):
        self._node = node

    def __str__(self):
        return self._node

    def _set_value(self, value):
        self._node.value = value

    def _get_value(self):
        return self._node.value

    value = property(_get_value, _set_value)

    @property
    def is_leaf(self):
        return self._node.is_leaf

    @property
    def separator(self):
        return self._node.separator

    @property
    def name(self):
        return self._node.name

    @property
    def leaves(self):
        for leaf in self._node.leaves:
            yield type(self)(leaf)

    def walk_to(self, node: "Node") -> Tuple:
        walker = anytree.walker.Walker()
        return tuple(
            type(self)(node_)
            for node_ in walker.walk(self._node, node._node)[2])

    @property
    def path(self):
        return self._node.separator + self._node.separator.join(
            [n.name for n in self._node.path]) + self._node.separator

    def get_descendant(self, path: str):
        resolver = anytree.Resolver('name')
        return type(self)(resolver.get(self._node, path))


class WebTemplateNode(Node):
    @staticmethod
    def create(dct: Dict) -> "WebTemplateNode":
        def _recursive_create(web_template_el):
            _node = anytree.Node(web_template_el['id'],
                                 rm_type=web_template_el['rmType'],
                                 required=web_template_el['min'] == 1,
                                 inf_cardinality=web_template_el['max'] == -1,
                                 annotations=web_template_el.get(
                                     'annotations', {}))

            children = []
            for child in web_template_el.get('children', []):
                children.append(_recursive_create(child)._node)
            _node.children = children

            return WebTemplateNode(_node)

        tree = dct['tree']
        node = _recursive_create(tree)
        return node

    @property
    def rm_type(self):
        return self._node.rm_type

    @property
    def required(self):
        return self._node.required

    @property
    def inf_cardinality(self):
        return self._node.inf_cardinality

    @property
    def annotations(self):
        return self._node.annotations

    @property
    def children(self):
        return [WebTemplateNode(child) for child in self._node.children]

    def __str__(self):
        return f'{self.path}, rm_type={self.rm_type},'\
            f'required={self.required}, inf_cardinality={self.inf_cardinality}'

    def __repr__(self):
        return f'{self.__class__.__name__}({str(self)})'


class Composition:
    def __init__(self, web_template: WebTemplateNode):
        self._web_template = web_template
        self._root = CompositionNode(
            anytree.Node(web_template.path.strip(web_template.separator)),
            web_template)

    @property
    def web_template(self):
        return self._web_template

    @property
    def root(self):
        return self._root

    def set_default(self, name: str, value: Union[int, str]):
        resolver = anytree.resolver.Resolver('name')
        leaves = [
            node for node in self._web_template.leaves if node.name == name
        ]
        for target in leaves:
            descendants = self._web_template.walk_to(target)
            path = self._root.separator.join([
                descendant.name if descendant.inf_cardinality is False else
                f'{descendant.name}:*' for descendant in descendants
            ][:-1])

            try:
                if not path:
                    self._root.add_descendant(
                        descendants[0].name).value = value
                else:
                    for node in resolver.glob(self._root._node, path):
                        descendant_path = node.separator.join([
                            CompositionNode(node, node.web_template).path, name
                        ])
                        self._root.add_descendant(
                            descendant_path).value = value
            except anytree.ChildResolverError as ex:
                ...
                #  self._root.add_descendant(target.path).value = value

    def as_flat(self):
        flat = {}
        for leaf in self._root.leaves:
            if leaf.web_template.is_leaf:
                flat[leaf.path.strip(leaf.separator)] = leaf.value
        return flat


class CompositionNode(Node):
    def __init__(self, node: anytree.Node, web_template_node: WebTemplateNode):
        super().__init__(node)
        self._node.web_template = web_template_node
        self._web_template_node = web_template_node
        self._resolver = anytree.Resolver('name')

    def __repr__(self):
        return '<CompositionNode %s>' % self._node

    @property
    def web_template(self):
        return self._web_template_node

    def add_child(self, name):
        web_template_node = self._web_template_node.get_descendant(name)
        if web_template_node.inf_cardinality:
            n_siblings = len(self._resolver.glob(self._node, f'{name}:*'))
            #  name = f'{name}:{n_siblings}'
            name = f'{name}:0'
            node = anytree.Node(name, parent=self._node)
        else:
            try:
                node = self._resolver.get(self._node, name)
            except anytree.ChildResolverError:
                node = anytree.Node(name, parent=self._node)
        return CompositionNode(node, web_template_node)

    def add_descendant(self, path):
        def _add_descendant(root, path_):
            try:
                node = self._resolver.get(root, path_)
            except anytree.ChildResolverError as ex:
                last_node = ex.node
                missing_child = ex.child
                web_template_node = last_node.web_template
                node = CompositionNode(
                    last_node, web_template_node).add_child(missing_child)

                path_to_remove = [n.name for n in last_node.path] + [
                    missing_child
                ] if path_.startswith('/') else [missing_child]

                for el in path_to_remove:
                    path_ = path_.replace(f'{el}', '', 1)

                path_ = path_.lstrip(root.separator)

                return _add_descendant(node._node, path_)
            else:
                web_template_node = node.web_template
                return CompositionNode(node, web_template_node)

        return _add_descendant(self._node, path)

    def _get_web_template(self):
        path = re.sub(r'\[\d+\]', '', self.path)
        return self._resolver.get(self._web_template_node, path)

    @property
    def leaves(self):
        for leaf in self._node.leaves:
            yield CompositionNode(leaf, leaf.web_template)


if __name__ == '__main__':
    import json
    webt = json.load(open("tests/resources/web_template.json", 'r'))
    web_template = WebTemplateNode.create(webt)
    comp = Composition(web_template)
    event0 = comp.root.add_descendant(
        '/test/molecular_markers/result_group/oncogenic_mutations_test/any_event'
    )
    event0.add_descendant('braf_pic3ca_her2_mutation_status').value = 1
    comp.root.add_descendant(
        '/test/molecular_markers/result_group/oncogenic_mutations_test/any_event/braf_pic3ca_her2_mutation_status'
    ).value = 2

    #  print('------------')
    #  comp.root.add_descendant(
    #      'molecular_markers/result_group/oncogenic_mutations_test/any_event/braf_pic3ca_her2_mutation_status'
    #  )
    print(comp.as_flat())

    print(web_template.get_descendant('*/language'))

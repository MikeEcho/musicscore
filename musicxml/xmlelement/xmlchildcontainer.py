import copy

from musicxml.util.core import convert_to_xml_class_name, cap_first
from musicxml.xmlelement.exceptions import XMLChildContainerFactoryError, XMLChildContainerWrongElementError, \
    XMLChildContainerChoiceHasAnotherChosenChild, XMLChildContainerMaxOccursError
from musicxml.xsd.xsdelement import XSDElement
from musicxml.xsd.xsdindicator import *
from musicxml.xsd.xsdtree import XSDTree
from tree.tree import Tree
import xml.etree.ElementTree as ET


def _convert_xsd_child_to_xsd_container(xsd_child):
    min_occurrences = xsd_child.get_attributes().get('minOccurs')
    max_occurrences = xsd_child.get_attributes().get('maxOccurs')
    copied_xml_child = copy.deepcopy(xsd_child)
    if min_occurrences is not None:
        copied_xml_child.get_attributes().pop('minOccurs')
    if max_occurrences is not None:
        copied_xml_child.get_attributes().pop('maxOccurs')
    if xsd_child.tag == 'element':
        return XMLChildContainer(content=XSDElement(copied_xml_child), min_occurrences=min_occurrences,
                                 max_occurrences=max_occurrences)
    elif xsd_child.tag == 'sequence':
        return XMLChildContainer(content=XSDSequence(copied_xml_child), min_occurrences=min_occurrences,
                                 max_occurrences=max_occurrences)
    elif xsd_child.tag == 'choice':
        return XMLChildContainer(content=XSDChoice(copied_xml_child), min_occurrences=min_occurrences,
                                 max_occurrences=max_occurrences)
    elif xsd_child.tag == 'group':
        xsd_group_name = 'XSDGroup' + ''.join([cap_first(partial) for partial in xsd_child.get_attributes()['ref'].split('-')])
        return XMLChildContainer(content=eval(xsd_group_name)(), min_occurrences=min_occurrences,
                                 max_occurrences=max_occurrences)
    else:
        raise NotImplementedError(xsd_child.tag)


def _check_if_container_requires_elements(xsd_container):
    if isinstance(xsd_container.content, XSDSequence):
        return _check_if_sequence_requires_elements(xsd_container)
    elif isinstance(xsd_container.content, XSDGroup):
        return _check_if_group_requires_elements(xsd_container)
    elif isinstance(xsd_container.content, XSDChoice):
        return _check_if_choice_requires_elements(xsd_container)
    else:
        raise NotImplementedError(xsd_container)


def _check_if_choice_requires_elements(xsd_container_choice):
    element_chosen = False
    for child in xsd_container_choice.get_children():
        if isinstance(child.content, XSDGroup):
            if child.get_children()[0].force_validate:
                _check_if_container_requires_elements(child.get_children()[0])
        elif child.force_validate:
            _check_if_container_requires_elements(child)
        else:
            if child.min_occurrences == 0:
                pass
            elif int(child.min_occurrences) == 1:
                if isinstance(child.content, XSDElement):
                    if len(child.content.xml_elements) == 0:
                        pass
                    elif len(child.content.xml_elements) == 1:
                        element_chosen = True
                    else:
                        raise NotImplementedError(child)
                else:
                    _check_if_container_requires_elements(child)
            else:
                raise NotImplementedError(f'child {child} with min_occurrence greater than 1')

    if element_chosen:
        xsd_container_choice.requirements_not_fulfilled = False


def _check_if_group_requires_elements(xsd_group_container):
    if xsd_group_container.min_occurrences == 0 and not xsd_group_container.get_children()[0].force_validate:
        return
    return _check_if_sequence_requires_elements(xsd_group_container.get_children()[0])


def _check_if_sequence_requires_elements(xsd_sequence_container):
    if xsd_sequence_container.force_validate:
        for child in xsd_sequence_container.get_children():
            if isinstance(child.content, XSDElement):
                if len(child.content.xml_elements) < child.min_occurrences:
                    child.requirements_not_fulfilled = True
                else:
                    pass
            else:
                _check_if_container_requires_elements(child)

    def validate_child(ch):
        if isinstance(ch.content, XSDElement):
            if child.choices_in_reversed_path:
                pass
            elif len(ch.content.xml_elements) < ch.min_occurrences:
                ch.requirements_not_fulfilled = True
            else:
                ch.requirements_not_fulfilled = False
        else:
            _check_if_container_requires_elements(ch)

    for child in xsd_sequence_container.get_children():
        if child.force_validate is True:
            _check_if_container_requires_elements(child)
        elif child.min_occurrences == 0:
            pass
        elif child.min_occurrences == 1:
            validate_child(child)
        else:
            raise NotImplementedError(f'child {child} with min_occurrence greater than 1')


class DuplicationXSDSequence(XSDSequence):
    sequence_xsd = """
            <xs:sequence xmlns:xs="http://www.w3.org/2001/XMLSchema">
            </xs:sequence>
    """

    def __init__(self):
        xsd_tree_ = XSDTree(ET.fromstring(self.sequence_xsd))
        super().__init__(xsd_tree_)


class XMLChildContainer(Tree):
    def __init__(self, content, min_occurrences=None, max_occurrences=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._content = None
        self._chosen_child = None
        self._required_element_names = None
        self._requirement_not_fulfilled = None
        self.min_occurrences = 1 if min_occurrences is None else int(min_occurrences)
        self.max_occurrences = 1 if max_occurrences is None else 'unbounded' if max_occurrences == 'unbounded' else int(max_occurrences)
        self.content = content
        self._force_validate = None
        self._parent_element = None

        self._populate_children()

    # private methods
    def _add_duplication_parent(self):

        if not self.get_parent():
            parent_container = XMLChildContainer(content=DuplicationXSDSequence())
            parent_container.add_child(self)
        elif not (isinstance(self.get_parent().content, DuplicationXSDSequence)):
            parent_container = XMLChildContainer(content=DuplicationXSDSequence())
            index = self.get_parent().get_children().index(self)
            parent = self.get_parent()
            parent.remove(self)
            parent.get_children().insert(index, parent_container)
            parent_container._parent = parent
            parent_container.add_child(self)
            if isinstance(parent.content, XSDChoice) and parent.chosen_child == self:
                parent.chosen_child = parent_container
        else:
            pass

    @staticmethod
    def _check_content_type(val):
        types = [XSDSequence, XSDChoice, XSDElement, XSDGroup]
        for type_ in types:
            if isinstance(val, type_):
                return
        raise TypeError(val)

    def _check_child_to_be_added(self, child):
        if not isinstance(child, XMLChildContainer):
            raise TypeError

    def _create_empty_copy(self):
        """
        Creates a copy without attached elements or duplicated nodes
        :return: XMLChildContainer
        """
        if isinstance(self.content, XSDChoice) or isinstance(self.content, XSDSequence):
            copied_content = self.content.__class__(self.content.xsd_tree)
        else:
            copied_content = eval(self.content.__class__.__name__)()
        return XMLChildContainer(copied_content, self.min_occurrences, self.max_occurrences)

    def _duplicate_parent_in_path(self):
        for node in list(self.reversed_path_to_root())[:-1]:
            if node.get_parent().max_occurrences == 'unbounded':
                return node.get_parent().duplicate()
        return None

    def _update_requirements_in_path(self):
        if not isinstance(self.content, XSDElement):
            raise ValueError
        if self.max_is_reached:
            self.requirements_not_fulfilled = False
        if self.content.xml_elements:
            for node in self.reversed_path_to_root():
                if node.get_parent():
                    if isinstance(node.get_parent().content, XSDChoice):
                        if node.get_parent().chosen_child:
                            if node.get_parent().chosen_child != node:
                                raise XMLChildContainerChoiceHasAnotherChosenChild
                            else:
                                break
                        else:
                            node.get_parent().chosen_child = node
                            if node.get_parent().requirements_not_fulfilled:
                                node.get_parent().requirements_not_fulfilled = False
                                break
                            node.get_parent().requirements_not_fulfilled = False
                    elif isinstance(node.get_parent().content, XSDSequence):
                        if node.get_parent().force_validate:
                            break
                        else:
                            node.get_parent().set_force_validate(node, True)

    def _populate_children(self):
        for xsd_child in [child for child in self.content.xsd_tree.get_children() if
                          child.tag != 'annotation' and child.tag != 'complexType']:
            container = _convert_xsd_child_to_xsd_container(xsd_child)
            self.add_child(container)

    def _set_requirement_not_fulfilled(self):
        for node in self.traverse():
            if isinstance(node.content, XSDChoice) and node.requirements_not_fulfilled is None and True not in [
                choice.requirements_not_fulfilled for choice in node.choices_in_reversed_path] and node.min_occurrences != 0:
                for leaf in node.iterate_leaves():
                    if leaf.content.xml_elements:
                        node._requirement_not_fulfilled = False
                if node._requirement_not_fulfilled is None:
                    for child in node.get_children():
                        if child.min_occurrences != 0:
                            node._requirement_not_fulfilled = True
                        break
            else:
                node._requirement_not_fulfilled = False

    # public properties

    @property
    def compact_repr(self):
        if isinstance(self.content, XSDSequence):
            type_ = 'Sequence'
            return f"{type_}@minOccurs={self.min_occurrences}@maxOccurs={self.max_occurrences}"

        if isinstance(self.content, XSDChoice):
            type_ = 'Choice'
            output = f"{type_}@minOccurs={self.min_occurrences}@maxOccurs={self.max_occurrences}"
            if self.requirements_not_fulfilled:
                output += '\n'
                output += self.get_indentation() + '    '
                output += '!Required!'
            return output

        if isinstance(self.content, XSDGroup):
            type_ = 'Group'
            return f"{type_}@name={self.content.name}@minOccurs={self.min_occurrences}@maxOccurs={self.max_occurrences}"

        if isinstance(self.content, XSDElement):
            type_ = 'Element'
            output = f"{type_}@name={self.content.name}@minOccurs={self.min_occurrences}@maxOccurs={self.max_occurrences}"
            for xml_element in self.content.xml_elements:
                output += '\n'
                output += self.get_indentation() + '    '
                output += xml_element.get_class_name()
            if self.requirements_not_fulfilled:
                output += '\n'
                output += self.get_indentation() + '    '
                output += '!Required!'
            return output

    @property
    def content(self) -> XSDElement:
        return self._content

    @content.setter
    def content(self, val: XSDElement):
        self._check_content_type(val)
        self._content = val

    @property
    def choices_in_reversed_path(self):
        return [node for node in list(self.reversed_path_to_root())[1:] if isinstance(node.content, XSDChoice)]

    @property
    def chosen_child(self):
        return self._chosen_child

    @chosen_child.setter
    def chosen_child(self, val):
        if not isinstance(self.content, XSDChoice):
            raise TypeError
        self._chosen_child = val

    @property
    def force_validate(self):
        return self._force_validate

    @property
    def max_is_reached(self):
        if not isinstance(self.content, XSDElement):
            raise TypeError
        if self.max_occurrences == 'unbounded':
            return False
        else:
            if len(self.content.xml_elements) == self.max_occurrences:
                return True
            elif len(self.content.xml_elements) > self.max_occurrences:
                raise ValueError
            else:
                return False

    @property
    def requirements_not_fulfilled(self):
        return self._requirement_not_fulfilled

    @requirements_not_fulfilled.setter
    def requirements_not_fulfilled(self, val: bool):
        if not isinstance(val, bool):
            raise TypeError
        self._requirement_not_fulfilled = val

    # public methods

    def add_element(self, xml_element, forward: int = 0):
        if self._requirement_not_fulfilled is None:
            self.check_required_elements()

        def select_valid_leaves(leaves):
            output = []
            choice_with_chosen_child = None
            for leaf in leaves:
                for n in leaf.reversed_path_to_root():
                    if n.get_parent() and isinstance(n.get_parent().content, XSDChoice) and n.get_parent().chosen_child:
                        choice_with_chosen_child = n.get_parent()
                        if n == choice_with_chosen_child.chosen_child:
                            output.append(leaf)
                        break

            if not choice_with_chosen_child:
                return leaves
            elif not output and choice_with_chosen_child.max_occurrences != 'unbounded':
                return None
            else:
                return output

        if 'XMLElement' not in [cls.__name__ for cls in xml_element.__class__.__mro__]:
            raise TypeError

        same_name_leaves = [leaf for leaf in self.iterate_leaves() if leaf.content.name == xml_element.name]

        if not same_name_leaves:
            raise XMLChildContainerWrongElementError()

        selected_same_name_leaves = select_valid_leaves(same_name_leaves)
        # print('selected_same_name_leaves', selected_same_name_leaves)
        if selected_same_name_leaves is None:
            raise XMLChildContainerChoiceHasAnotherChosenChild()

        if selected_same_name_leaves == []:
            duplicated_parent = same_name_leaves[-1]._duplicate_parent_in_path()
            if duplicated_parent:
                selected_same_name_leaves = [leaf for leaf in duplicated_parent.iterate_leaves() if
                                             leaf.content.name == xml_element.name and not
                                             leaf.max_is_reached]
            else:
                raise XMLChildContainerChoiceHasAnotherChosenChild

        if forward:
            selected = same_name_leaves[forward]
            if selected not in selected_same_name_leaves:
                raise XMLChildContainerChoiceHasAnotherChosenChild('Wrong forwarding')
        else:
            selected_same_name_leaves_max_not_reached = [leaf for leaf in selected_same_name_leaves if not leaf.max_is_reached]
            if not selected_same_name_leaves_max_not_reached:
                duplicated_parent = selected_same_name_leaves[-1]._duplicate_parent_in_path()
                if duplicated_parent:
                    selected_same_name_leaves_max_not_reached = [leaf for leaf in duplicated_parent.iterate_leaves() if leaf.content.name ==
                                                                 xml_element.name and not leaf.max_is_reached]
                else:
                    raise XMLChildContainerMaxOccursError()

            selected = selected_same_name_leaves_max_not_reached[0]

        selected.content.add_xml_element(xml_element)
        selected._update_requirements_in_path()
        self.check_required_elements()
        return selected

    def check_required_elements(self):
        if self._requirement_not_fulfilled is None:
            self._set_requirement_not_fulfilled()
        _check_if_container_requires_elements(self)
        for node in self.traverse():
            if node.requirements_not_fulfilled:
                return True
        return False

    def duplicate(self):
        if not isinstance(self.content, XSDSequence) and not isinstance(self.content, XSDChoice) and not isinstance(self.content, XSDGroup):
            raise TypeError(self.content)

        if self.max_occurrences != 'unbounded':
            raise ValueError

        self._add_duplication_parent()

        copied_self = self._create_empty_copy()
        copied_self._parent = self.get_parent()
        self.get_parent().add_child(copied_self)
        return copied_self

    def get_leaves(self, function=None):
        if isinstance(self.content, XSDElement):
            if function:
                return function(self)
            else:
                return self.content
        elif isinstance(self.content, XSDGroup):
            return self.get_children()[0].get_leaves(function=function)
        elif isinstance(self.content, XSDSequence) or isinstance(self.content, XSDChoice):
            output = [node.get_leaves(function=function) for node in self.get_children() if node.get_leaves(function=function)]
            try:
                if not output or set(output) == {None}:
                    return None
            except TypeError:
                pass
            if len(output) == 1:
                return output[0]
            return output if isinstance(self.content, XSDSequence) else tuple(output)
        else:
            raise NotImplementedError

    def get_parent_element(self):
        return self._parent_element

    def get_required_element_names(self):
        def func(leaf):
            if leaf.requirements_not_fulfilled is True:
                return convert_to_xml_class_name(leaf.content.name)

            elif leaf.min_occurrences != 0 and True in [choice.requirements_not_fulfilled for choice in leaf.choices_in_reversed_path]:
                if isinstance(leaf.get_parent().content, XSDSequence) and leaf.get_parent().min_occurrences == 0 and not leaf.get_parent(

                ).force_validate:
                    pass
                else:
                    return convert_to_xml_class_name(leaf.content.name)

        self.check_required_elements()
        return self.get_leaves(func)

    def set_force_validate(self, node, val):
        self._force_validate = val
        for child in [ch for ch in self.get_children() if ch != node]:
            for n in child.traverse():
                if isinstance(n.content, XSDChoice):
                    if n.min_occurrences != 0 and not n.chosen_child:
                        n.requirements_not_fulfilled = True
                    break
                if isinstance(n.content, XSDSequence) and n.min_occurrences != 0 and not (isinstance(n.get_parent().content, XSDGroup) and
                                                                                          n.get_parent().min_occurrences == 0):
                    n._force_validate = val

    def __repr__(self):
        return f"XMLChildContainer:{self.compact_repr} {self.get_coordinates_in_tree()}"


class XMLChildContainerFactory:
    def __init__(self, complex_type):
        self._child_container = None
        self._create_child_container(complex_type)

    def _create_child_container(self, complex_type):
        if 'XSDComplexType' not in [cls.__name__ for cls in complex_type.__mro__]:
            raise TypeError
        if not complex_type.get_xsd_indicator():
            raise XMLChildContainerFactoryError(f'complex_type {complex_type} has no xsd_indicator.')
        child_container = XMLChildContainer(*complex_type.get_xsd_indicator())
        self._child_container = child_container

    def get_child_container(self):
        return self._child_container
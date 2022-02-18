from musicxml.xmlelement.xmlelement import XMLScorePartwise, XMLPartList, XMLCredit, XMLCreditWords

from musictree.musictree import MusicTree
from musictree.quarterduration import QuarterDuration
from musictree.xmlwrapper import XMLWrapper

TITLE = {'font_size': 24, 'default_x': {'A4': {'portrait': 616}}, 'default_y': {'A4': {'portrait': 1573}}, 'justify': 'center',
         'valign': 'top'}

SUBTITLE = {'font_size': 18, 'default_x': {'A4': {'portrait': 616}}, 'default_y': {'A4': {'portrait': 1508}}, 'halign': 'center',
            'valign': 'top'}


class Score(MusicTree, XMLWrapper):
    _ATTRIBUTES = {'version', 'title', 'subtitle'}

    def __init__(self, version='4.0', title=None, subtitle=None, *args, **kwargs):
        super().__init__()
        self._xml_object = XMLScorePartwise(*args, **kwargs)
        self._xml_object.add_child(XMLPartList())
        self._version = None
        self._title = None
        self._subtitle = None
        self.version = version

        self.title = title
        self.subtitle = subtitle
        self._possible_subdivisions = {QuarterDuration(1, 4): [2, 3], QuarterDuration(1, 2): [2, 3, 4, 5], QuarterDuration(1): [2, 3, 4,
                                                                                                                                5, 6, 7, 8]}

    def _get_title_attributes(self):
        output = TITLE.copy()
        output['default_x'] = TITLE['default_x']['A4']['portrait']
        output['default_y'] = TITLE['default_y']['A4']['portrait']
        return output

    def _get_subtitle_attributes(self):
        output = SUBTITLE.copy()
        output['default_x'] = SUBTITLE['default_x']['A4']['portrait']
        output['default_y'] = SUBTITLE['default_y']['A4']['portrait']
        return output

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, val):
        self._version = str(val)
        self.xml_object.version = self.version

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, val):
        if val is not None:
            if self._title is None:
                credit = self.xml_object.add_child(XMLCredit(page=1))
                credit.xml_credit_type = 'title'
                self._title = credit.add_child(XMLCreditWords(value_=val, **self._get_title_attributes()))
            else:
                self._title.value_ = val
        else:
            if self._title is None:
                pass
            else:
                credit = self._title.up
                credit.up.remove(credit)
                self._title = None

    @property
    def subtitle(self):
        return self._subtitle

    @subtitle.setter
    def subtitle(self, val):
        if val is not None:
            if self._subtitle is None:
                credit = self.xml_object.add_child(XMLCredit(page=1))
                credit.xml_credit_type = 'subtitle'
                self._subtitle = credit.add_child(XMLCreditWords(value_=val, **self._get_subtitle_attributes()))
            else:
                self._subtitle.value_ = val
        else:
            if self._subtitle is None:
                pass
            else:
                credit = self._subtitle.up
                credit.up.remove(credit)
                self._subtitle = None

    def add_child(self, child):
        super().add_child(child)
        self.xml_object.add_child(child.xml_object)
        self.xml_part_list.xml_score_part = child.score_part.xml_object
        return child

    def export_xml(self, path):
        with open(path, '+w') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE score-partwise PUBLIC
    "-//Recordare//DTD MusicXML 4.0 Partwise//EN"
    "http://www.musicxml.org/dtds/partwise.dtd">
""")
            f.write(self.to_string())

    def update(self):
        for p in self.get_children():
            p.update()

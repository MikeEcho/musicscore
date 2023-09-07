from pathlib import Path

from musictree import Score, Chord
from musictree.tests.util import IdTestCase
from musictree.util import XML_DIRECTION_TYPE_CLASSES
from musicxml.xmlelement.xmlelement import XMLSymbol, XMLDynamics, XMLWedge, XMLDashes, XMLBracket, XMLPedal, \
    XMLMetronome, XMLBeatUnit, XMLPerMinute, XMLOctaveShift, XMLHarpPedals, XMLPedalTuning, XMLPedalStep, XMLPedalAlter, \
    XMLStringMute, XMLScordatura, XMLAccord, XMLTuningOctave, XMLTuningStep, XMLImage, XMLPrincipalVoice, XMLPercussion, \
    XMLWood, XMLStaffDivide

dynamics = ['f', 'ff', 'fff', 'ffff', 'fffff', 'ffffff', 'fp', 'fz', 'mf', 'mp', 'p', 'pf', 'pp', 'ppp', 'pppp',
            'ppppp', 'pppppp', 'rf', 'rfz', 'sf', 'sffz', 'sfp', 'sfpp', 'sfz', 'sfzp']


class TestDynamics(IdTestCase):
    def test_dynamics(self):
        score = Score(title='Dynamics')
        p = score.add_part('part-1')
        p.name = ''
        for d in dynamics:
            chord = Chord(midis=60, quarter_duration=4)
            chord.add_dynamics(d)
            p.add_chord(chord)
        wedge_chords = ch1, ch2 = [Chord(midis=60, quarter_duration=4), Chord(midis=60, quarter_duration=4)]
        ch1.add_dynamics('p')
        ch2.add_dynamics('ff')
        ch1.add_wedge('crescendo')
        ch2.add_wedge('stop')

        for chord in wedge_chords:
            p.add_chord(chord)
        xml_path = 'test_9a_dynamics.xml'
        score.export_xml(xml_path)

    def test_direction_types(self):
        score = Score(title='Dynamics')
        p = score.add_part('part-1')
        for dt_class in [cl for cl in XML_DIRECTION_TYPE_CLASSES if cl != XMLDynamics]:
            if dt_class == XMLSymbol:
                dt_obj = dt_class('0')
            elif dt_class == XMLWedge:
                dt_obj = dt_class(type='crescendo')
            elif dt_class == XMLDashes:
                dt_obj = dt_class(type='start')
            elif dt_class == XMLBracket:
                dt_obj = dt_class(type='start', line_end='none')
            elif dt_class == XMLPedal:
                dt_obj = dt_class(type='start')
            elif dt_class == XMLMetronome:
                dt_obj = dt_class()
                dt_obj.add_child(XMLBeatUnit('quarter'))
                dt_obj.add_child(XMLPerMinute('120'))
            elif dt_class == XMLOctaveShift:
                dt_obj = dt_class(type='up')
            elif dt_class == XMLHarpPedals:
                dt_obj = dt_class()
                pt = dt_obj.add_child(XMLPedalTuning())
                pt.add_child(XMLPedalStep('A'))
                pt.add_child(XMLPedalAlter(1))
            elif dt_class == XMLStringMute:
                dt_obj = dt_class(type='on')
            elif dt_class == XMLScordatura:
                dt_obj = dt_class()
                acc = dt_obj.add_child(XMLAccord())
                acc.add_child(XMLTuningStep('A'))
                acc.add_child(XMLTuningOctave(0))
            elif dt_class == XMLImage:
                # dt_obj = dt_class(source='www.example.com')
                continue
            elif dt_class == XMLPrincipalVoice:
                dt_obj = dt_class(type='start', symbol='none')
            elif dt_class == XMLPercussion:
                dt_obj = dt_class()
                dt_obj.add_child(XMLWood('cabasa'))
            elif dt_class == XMLStaffDivide:
                dt_obj = dt_class(type='up')
            else:
                dt_obj = dt_class()

            chord = Chord(midis=60, quarter_duration=4)
            chord.add_direction_type(dt_obj)
            p.add_chord(chord)
        xml_path = 'test_9b_directions_types.xml'
        score.export_xml(xml_path)
from pathlib import Path

from musictree import Score, Time, Chord, B

"""
Compound time signatures with separate fractions displayed: 3/8+2/8+3/4 and 5/2+1/8.
"""

score = Score()
part = score.add_part('part')
part.add_measure(time=Time(3, 8, 2, 8, 3, 4))
part.add_measure(time=Time(5, 2, 1, 8))
[part.add_chord(Chord(B(4), x / 2)) for x in [1, 1, 1, 1, 1, 2, 2, 2]]
[part.add_chord(Chord(B(4), x)) for x in [8, 2, 0.5]]

xml_path = Path(__file__).with_suffix('.xml')
score.export_xml(xml_path)

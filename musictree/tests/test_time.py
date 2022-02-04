from unittest import TestCase

from fractions import Fraction

from musictree.time import Time


class TestTime(TestCase):
    def test_time_init(self):
        t = Time()
        expected = """<time>
  <beats>4</beats>
  <beat-type>4</beat-type>
</time>
"""
        assert t.to_string() == expected
        t.xml_beats = '3'
        expected = """<time>
  <beats>3</beats>
  <beat-type>4</beat-type>
</time>
"""
        assert t.to_string() == expected
        t = Time(6, 8, 3, 4)
        expected = """<time>
  <beats>6</beats>
  <beat-type>8</beat-type>
  <beats>3</beats>
  <beat-type>4</beat-type>
</time>
"""
        assert t.to_string() == expected

    def test_change_fractions(self):
        t = Time()
        t.signatures = [7, 8, 3, 4]
        expected = """<time>
  <beats>7</beats>
  <beat-type>8</beat-type>
  <beats>3</beats>
  <beat-type>4</beat-type>
</time>
"""
        assert t.to_string() == expected
        t.signatures = None
        expected = """<time>
  <beats>4</beats>
  <beat-type>4</beat-type>
</time>
"""
        assert t.to_string() == expected
        t.signatures = [2, 4]
        expected = """<time>
  <beats>2</beats>
  <beat-type>4</beat-type>
</time>
"""
        assert t.to_string() == expected
        t = Time()

    def test_time_actual_signatures(self):
        t = Time()
        assert t.actual_signatures == [1, 4, 1, 4, 1, 4, 1, 4]
        t.signatures = [3, 4]
        assert t.actual_signatures == [1, 4, 1, 4, 1, 4]
        t.actual_signatures = [3, 4]
        assert t.actual_signatures == [3, 4]
        t.signatures = [3, 2]
        assert t.actual_signatures == [3, 4]
        t.reset_actual_signatures()
        assert t.actual_signatures == [1, 2, 1, 2, 1, 2]

    def test_get_beats_quarter_durations(self):
        t = Time()
        assert t.get_beats_quarter_durations() == [Fraction(1)] * 4
        t.signatures = [3, 4]
        assert t.get_beats_quarter_durations() == [Fraction(1)] * 3
        t.signatures = [6, 8]
        assert t.get_beats_quarter_durations() == [Fraction(3, 2)] * 2
        t.actual_signatures = [1, 8] * 6
        assert t.get_beats_quarter_durations() == [Fraction(1, 2)] * 6
        t.signatures = [3, 4, 2, 8]
        t.reset_actual_signatures()
        assert t.get_beats_quarter_durations() == [Fraction(1)] * 3 + [Fraction(1, 2)] * 2

from unittest import TestCase

from musictree.staff import Staff
from musictree.voice import Voice


class TestStaff(TestCase):
    def test_staff_init(self):
        st = Staff()
        assert st.value is None
        assert st.xml_object.value is None
        st = Staff(3)
        assert st.xml_object.value == 3
        assert st.value == 3
        st.value = 2
        assert st.xml_object.value == 2
        st.xml_object.value = None
        assert st.value is None
        assert st.xml_object.value is None

    def test_add_voice(self):
        st = Staff()
        assert [child.value for child in st.get_children()] == []
        st.add_child(Voice())
        assert [child.value for child in st.get_children()] == [1]
        st.add_child(Voice())
        assert len(st.get_children()) == 2
        assert [child.value for child in st.get_children()] == [1, 2]

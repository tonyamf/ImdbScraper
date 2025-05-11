import unittest
from phonebook import Phonebook

class PhonebookTest(unittest.TestCase):
    

    def setUp(self):
        self.phonebook = Phonebook()   


    def test_lookup_entry_by_name(self):
        self.phonebook.add("Bob", "12345")
        self.assertEqual("12345", self.phonebook.lookup("Bob"))

    def test_missing_entry_raises_KeyError(self):
        with self.assertRaises(KeyError):
            self.phonebook.lookup('missing')

    # @unittest.skip("WIP")
    def test_empty_phonebook_is_consistent(self):
        self.phonebook = Phonebook()
        self.assertTrue(self.phonebook.is_consistent())


    
import unittest
from bytebloom import SafeRunner, translate

class ByteBloomTests(unittest.TestCase):
    def test_assignment_and_expression(self):
        r = SafeRunner(); r.run('make total = 4 * 5')
        self.assertEqual(r.env['total'], 20)
    def test_if_else(self):
        r = SafeRunner(); r.run('make n = 9\nwhen n > 5:\n    make result = "big"\notherwise:\n    make result = "small"')
        self.assertEqual(r.env['result'], 'big')
    def test_loop(self):
        r = SafeRunner(); r.run('times 4:\n    make answer = 12')
        self.assertEqual(r.env['answer'], 12)
    def test_translation(self):
        self.assertIn('print("Hi")', translate('display "Hi"'))
    def test_unknown_variable(self):
        with self.assertRaises(NameError): SafeRunner().run('display missing')

if __name__ == '__main__': unittest.main()

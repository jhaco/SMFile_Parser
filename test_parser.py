import smfile_parser as parse
import unittest

TEST_FILE_FORMATTED = "test-file_"
TEST_FILE_WITH_RANDOM_CHARS = "/|`:t~;E?]@[sT(->f.!+i<.#L,)$=e%^_^*.ext"

class TestParser(unittest.TestCase):
    def test_format_file_name(self):
        self.assertEqual(parse.format_file_name(TEST_FILE_WITH_RANDOM_CHARS), TEST_FILE_FORMATTED)

    def test_convert_note(self):
        self.assertEqual(parse.convert_note("MKLF"), "0000")
        self.assertEqual(parse.convert_note("K42L"), "0120")

    def test_calculate_timing(self):
        measure = [True, False, False, True]
        measure_index = 2
        bpm = 200.000
        offset = 0.009

        timings = parse.calculate_timing(measure, measure_index, bpm, offset)
        self.assertTrue(all(float(time) >= 0 for time in timings))
        self.assertEqual(timings, ["2.391", "3.291"])

    #def test_parse_sm(self):


if __name__ == '__main__':
    unittest.main()
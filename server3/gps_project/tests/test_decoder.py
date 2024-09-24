import unittest
from src.decoder.gps_decoder import Decoder

class TestDecoder(unittest.TestCase):
    def setUp(self):
        self.sample_payload = "000000000000003608010000016B40D8EA30010000000000000000000000000000000105021503010101425E0F01F10000601A014E0000000000000000010000C7CF"
        self.imei = "123456789012345"

    def test_decode_data(self):
        decoder = Decoder(self.sample_payload, self.imei)
        records = decoder.decode_data()
        
        self.assertIsNotNone(records)
        self.assertEqual(len(records), 1)
        
        record = records[0]
        self.assertEqual(record['IMEI'], self.imei)
        self.assertIn('DateTime', record)
        self.assertIn('Priority', record)
        self.assertIn('Location', record)
        self.assertIn('I/O Data', record)

    def test_parse_avl_record(self):
        decoder = Decoder(self.sample_payload, self.imei)
        decoder.index = 16  # Skip header
        record = decoder.parse_avl_record()
        
        self.assertIsNotNone(record)
        self.assertEqual(record['IMEI'], self.imei)
        self.assertEqual(record['Priority'], 1)
        self.assertEqual(record['Location']['Satellites'], 0)
        self.assertEqual(record['Location']['Speed'], 0)

    def test_parse_io_data(self):
        decoder = Decoder(self.sample_payload, self.imei)
        decoder.index = 56  # Position of IO data in sample payload
        io_data = decoder.parse_io_data()
        
        self.assertIsNotNone(io_data)
        self.assertIn('Event IO ID', io_data)
        self.assertEqual(io_data['Event IO ID'], 1)

if __name__ == '__main__':
    unittest.main()
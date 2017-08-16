import unittest
import tiles as t
import shutil
import glob
import os


class TilesTestCase(unittest.TestCase):

    def test_eTILES(self):
        base = os.path.dirname(os.path.abspath(__file__))
        os.makedirs("eres")
        et = t.eTILES(filename="%s/sample_net_etiles.tsv" % base, obs=1, path="eres")
        et.execute()

        count = 0
        for _ in glob.glob("eres/graph*"):
            count += 1
        self.assertEqual(count, 6)

        shutil.rmtree("eres")

    def test_TILES(self):
        base = os.path.dirname(os.path.abspath(__file__))

        os.makedirs("res")
        et = t.TILES(filename="%s/sample_net_tiles.tsv" % base, obs=1, path="res")
        et.execute()

        count = 0
        for _ in glob.glob("res/graph*"):
            count += 1
        self.assertEqual(count, 6)

        shutil.rmtree("res")

        os.makedirs("res2")
        et = t.TILES(filename="%s/sample_net_tiles.tsv" % base, obs=1, path="res2", ttl=86400)
        et.execute()

        count = 0
        for _ in glob.glob("res2/graph*"):
            count += 1
        self.assertEqual(count, 6)

        shutil.rmtree("res2")

if __name__ == '__main__':
    unittest.main()

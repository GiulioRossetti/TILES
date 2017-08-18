import unittest
import tiles as t
import shutil
import glob
import os


class TilesTestCase(unittest.TestCase):

    def test_eTILES(self):
        base = os.getcwd()
        os.makedirs("eres")
        et = t.eTILES(filename="%s/sample_net_etiles.tsv" % base, obs=1, path="eres")
        et.execute()

        count = 0
        for _ in glob.glob("eres/graph*"):
            count += 1
        self.assertEqual(count, 6)

        shutil.rmtree("eres")

    def test_TILES(self):
        base = os.getcwd()
        os.makedirs("res")
        et = t.TILES(filename="%s/sample_net_tiles.tsv" % base, obs=1, path="res")
        et.execute()

        count = 0
        for _ in glob.glob("res/graph*"):
            count += 1
        self.assertEqual(count, 6)

        shutil.rmtree("res")

        os.makedirs("res2")
        et = t.TILES(filename="%s/sample_net_tiles.tsv" % base, obs=1, path="res2", ttl=1)
        et.execute()

        count = 0
        for _ in glob.glob("res2/graph*"):
            count += 1
        self.assertEqual(count, 6)

        shutil.rmtree("res2")

        os.makedirs("res3")
        et = t.TILES(filename="%s/sample_net_tiles.tsv" % base, obs=1, path="res3", ttl=2)
        et.execute()

        count = 0
        for _ in glob.glob("res3/graph*"):
            count += 1
        self.assertEqual(count, 6)

        shutil.rmtree("res3")

    def test_TILES_rem(self):

        os.makedirs("res4")
        et = t.TILES(filename="%s/gen_simple.tsv" % base, obs=30, path="res4", ttl=90)
        et.execute()

        count = 0
        for _ in glob.glob("res4/graph*"):
            count += 1

        self.assertEqual(count, 34)
        shutil.rmtree("res4")

if __name__ == '__main__':
    unittest.main()

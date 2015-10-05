import os
import shutil
import tempfile

from unittest import TestCase

from regparser.notice import xml as notice_xml
import settings


class NoticeXMLLocalCopiesTests(TestCase):
    """Tests specifically related to xml.local_copies, which has significant
    setup/teardown"""
    def setUp(self):
        self.dir1 = tempfile.mkdtemp()
        self.dir2 = tempfile.mkdtemp()
        self._original_local_xml_paths = settings.LOCAL_XML_PATHS
        settings.LOCAL_XML_PATHS = [self.dir1, self.dir2]
        self.url = 'http://example.com/some/url'

    def tearDown(self):
        settings.LOCAL_XML_PATHS = self._original_local_xml_paths
        shutil.rmtree(self.dir1)
        shutil.rmtree(self.dir2)

    def test_empty(self):
        """If no copy is present, we get an empty list"""
        self.assertEqual([], notice_xml.local_copies(self.url))

        os.mkdir(os.path.join(self.dir1, "some"))
        self.assertEqual([], notice_xml.local_copies(self.url))

    def test_order(self):
        """The first source will override the second"""
        url = 'http://example.com/some/url'
        paths = []
        for d in (self.dir1, self.dir2):
            os.mkdir(os.path.join(d, "some"))
            paths.append(os.path.join(d, "some", "url"))

        with open(paths[1], "w") as f:
            f.write('aaaaa')
        self.assertEqual([paths[1]], notice_xml.local_copies(url))

        with open(paths[0], "w") as f:
            f.write('bbbbb')
        self.assertEqual([paths[0]], notice_xml.local_copies(url))

    def test_splits(self):
        """If multiple files are present from a single source, return all"""
        url = 'http://example.com/xml/503.xml'
        os.mkdir(os.path.join(self.dir1, 'xml'))
        paths = []
        for i in range(3):
            path = os.path.join(self.dir1, 'xml', '503-{}.xml'.format(i + 1))
            paths.append(path)
            with open(path, 'w') as f:
                f.write(str(i)*10)

        self.assertEqual(set(paths), set(notice_xml.local_copies(url)))

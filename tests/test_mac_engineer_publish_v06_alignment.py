from __future__ import annotations

import unittest

import tools.mac_engineer_publish_v06_alignment as publish


class MacEngineerPublishV06AlignmentTests(unittest.TestCase):
    def test_publication_scope_is_exact(self):
        self.assertEqual(
            publish.REPOSITORY,
            "engurulabory/enguru-mac-engineer",
        )
        self.assertEqual(
            publish.BRANCH,
            "feature/v06-version-branding-alignment",
        )
        self.assertEqual(publish.BASE, "main")

    def test_publication_requires_prepared_evidence(self):
        self.assertEqual(
            publish.PREPARED.name,
            "package6-product-v06-alignment-prepared.json",
        )

    def test_publication_writes_separate_evidence(self):
        self.assertEqual(
            publish.OUTPUT.name,
            "package6-product-v06-alignment-publication.json",
        )


if __name__ == "__main__":
    unittest.main()

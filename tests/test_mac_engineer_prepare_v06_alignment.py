from __future__ import annotations

import unittest

import tools.mac_engineer_prepare_v06_alignment as align


class MacEngineerPrepareV06AlignmentTests(unittest.TestCase):
    def test_target_version_is_v06(self):
        self.assertEqual(align.TARGET_VERSION, "0.6")

    def test_alignment_branch_is_product_scoped(self):
        self.assertEqual(
            align.BRANCH,
            "feature/v06-version-branding-alignment",
        )

    def test_branding_asset_path_is_canonicalized(self):
        self.assertEqual(
            align.PRODUCT_ASSET.relative_to(align.PRODUCT_RUNTIME).as_posix(),
            "static/engineer-emblem.png",
        )
        self.assertEqual(
            align.RUNTIME_ASSET.relative_to(align.RUNTIME_RUNTIME).as_posix(),
            "static/engineer-emblem.png",
        )

    def test_alignment_changes_only_product_source_paths(self):
        self.assertTrue(
            align.INFO.is_relative_to(align.PRODUCT)
        )
        self.assertTrue(
            align.PRODUCT_ASSET.is_relative_to(align.PRODUCT)
        )


if __name__ == "__main__":
    unittest.main()

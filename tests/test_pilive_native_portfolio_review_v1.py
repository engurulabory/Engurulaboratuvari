"""Regression from reviewed real Mac Core results; never product acceptance."""
import copy
import json
from pathlib import Path
import unittest
from tools import pilive_core_snapshot_adapter_v1 as adapter


def captured():
    return json.loads((Path(__file__).parent / 'fixtures/pilive_native_portfolio_review_v1.json').read_text())


class NativePortfolioReviewTests(unittest.TestCase):
    def test_exact_native_model_digest_and_p02_authority(self):
        d = captured()
        s = adapter.build_portfolio(d['registry'], d['facts'], **d['identity'])
        self.assertEqual(s['projectionDigest'], d['expectedProjectionDigest'])
        self.assertEqual(s['factCoverage'], {'projects': 15, 'sourceBoundObservations': 15, 'qualifiedCounters': 14})
        p02 = next(r for r in s['projects'] if r['key'] == 'plive-p02-user-screen')
        self.assertEqual((p02['done'], p02['total'], p02['percent'], p02['activeItem']), (0, 12, 0.0, 'P02.S01.01'))
        self.assertTrue(all(r['officialAcceptance'] == 'HOLD' and not r['closed'] for r in s['projects']))
        core = next(r for r in s['projects'] if r['key'] == 'progress-core')
        self.assertEqual((core['percent'], core['finish']), (100.0, 'HOLD'))

    def test_real_unverified_visual_items_keep_focus_and_na_counter(self):
        d = captured()
        fact = d['facts']['visual-cockpit-premium-v1']
        self.assertEqual((fact['summary']['declaredPass'], fact['verify']['evidencedPass'], fact['verify']['unverifiedPass']), (26, 24, 2))
        s = adapter.build_portfolio(d['registry'], d['facts'], **d['identity'])
        row = next(r for r in s['projects'] if r['key'] == 'visual-cockpit-premium-v1')
        self.assertEqual(row['activeItem'], 'P04.03_HUMAN_THRESHOLD')
        self.assertEqual(row['status'], 'HOLD')
        self.assertTrue(all(row[k] is None for k in ('done', 'total', 'percent')))

    def test_native_facts_reject_drift_and_isolate_corruption_or_interruption(self):
        for kind in ('revision', 'sha', 'identity', 'counter', 'interruption'):
            d = copy.deepcopy(captured())
            with self.subTest(kind=kind):
                if kind == 'revision':
                    d['identity']['revision_after'] = '0' * 40
                elif kind == 'sha':
                    d['identity']['pins_after']['tools/enguru_progress.py'] = '0' * 64
                elif kind == 'identity':
                    d['facts']['academy']['summary']['projectId'] = 'OTHER'
                elif kind == 'counter':
                    d['facts']['academy']['verify']['countedPass'] = True
                else:
                    d['facts']['academy'] = {'error': 'CORE_TIMEOUT'}
                if kind in ('revision', 'sha'):
                    with self.assertRaises(adapter.Hold):
                        adapter.build_portfolio(d['registry'], d['facts'], **d['identity'])
                else:
                    s = adapter.build_portfolio(d['registry'], d['facts'], **d['identity'])
                    self.assertEqual(s['factCoverage']['qualifiedCounters'], 13)
                    self.assertIsNone(next(r for r in s['projects'] if r['key'] == 'academy')['done'])
        d = captured()
        s = adapter.build_portfolio(d['registry'], d['facts'], **d['identity'])
        self.assertEqual(adapter.freshness(s, now='2026-10-26T07:00:00Z', stale_after_seconds=60)['state'], 'STALE')


if __name__ == '__main__':
    unittest.main()

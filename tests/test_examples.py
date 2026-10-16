from pathlib import Path
from decimal import Decimal
import json, shutil, tempfile, unittest
from programs.queue_simulation import simulate, quantile_nearest_rank
from programs.cost_model import month_cost, cumulative_effect
from programs.verify_bundle import verify_bundle
from programs.reliability import zero_event_upper

ROOT=Path(__file__).resolve().parents[1]
class BookExamples(unittest.TestCase):
    def test_queue_deadline_and_types(self):
        arrivals=[i/18 for i in range(540)]
        self.assertEqual(simulate(arrivals, .07, 2, .45)["violations"],0)
        self.assertGreater(simulate(arrivals, .07, 1, .45)["violations"],0)
        for bad in ("2", True, 0, 1.2):
            with self.assertRaises(ValueError):simulate(arrivals,.07,bad,.45)
        self.assertEqual(quantile_nearest_rank([1,2,3,4],.95),4)
    def test_cost_balance_calendar_and_sensitivity(self):
        base=month_cost()
        self.assertEqual(base["auto_on_time"],Decimal("1630368"))
        self.assertEqual(base["manual"],Decimal("369632"))
        self.assertEqual(base["effect"],Decimal("412776"))
        self.assertEqual(month_cost(timely="0.995")["effect"],Decimal("407880"))
        path=cumulative_effect([600000,1200000,1600000]+[2000000]*33)
        self.assertEqual(path[-1][1],Decimal("9670327.2"))
        self.assertEqual(next(m for m,v in path if v>0),13)
        with self.assertRaises(ValueError):month_cost(coverage="1.01")
    def test_integrity_tamper_and_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            b=Path(tmp)/"bundle";shutil.copytree(ROOT/"examples/bundle",b)
            m=b/"manifest.json";self.assertTrue(verify_bundle(b,m))
            spec=json.loads(m.read_text());spec["files"]={k:v.upper() for k,v in spec["files"].items()};m.write_text(json.dumps(spec))
            self.assertTrue(verify_bundle(b,m))
            (b/"model.bin").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError,"digest mismatch"):verify_bundle(b,m)
            shutil.copyfile(ROOT/"examples/bundle/model.bin",b/"model.bin")
            spec["files"]["../outside"]="0"*64;m.write_text(json.dumps(spec))
            with self.assertRaisesRegex(ValueError,"path outside"):verify_bundle(b,m)
    def test_binomial_bound(self):
        self.assertAlmostEqual(zero_event_upper(10000),1-.05**(1/10000),places=14)
        for n in (0,True,1.5):
            with self.assertRaises(ValueError):zero_event_upper(n)

if __name__=="__main__":unittest.main()

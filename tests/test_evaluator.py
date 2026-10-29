import unittest
from evaluate import evaluate
C=dict(id='A',split='development',prompt='Convert 1000 L/s',kind='numeric',expected_value=1,expected_unit='m3/s',abs_tolerance=0.001,rel_tolerance=0,allowed_source_ids=['SYN'],reference_reasoning='1000 / 1000 = 1.')
A=dict(id='A',value=1000,unit='L/s',abstain=False,source_ids=['SYN'],reasoning='Divide litres by 1000.')

class EvaluatorTests(unittest.TestCase):
    def result(self,c=C,a=A):
        return evaluate([c],[a])['results'][0]

    def test_equivalent_units(self):
        self.assertTrue(self.result()['all_structural_checks_pass'])

    def test_wrong_dimension_and_number(self):
        for a in [dict(A,unit='m'),dict(A,value=100)]:
            self.assertFalse(self.result(a=a)['checks']['task_result'])

    def test_missing_answer_counted_in_denominator(self):
        s=evaluate([C],[])['summary']['all']
        self.assertEqual((s['cases'],s['answers_present'],s['structural_pass_rate']),(1,0,0))

    def test_duplicate_unknown_id(self):
        for answers in [[A,A],[dict(A,id='other')]]:
            with self.assertRaises(ValueError):
                evaluate([C],answers)

    def test_nan_and_bool_rejected(self):
        for value in [float('nan'),True]:
            with self.assertRaises(ValueError):
                self.result(a=dict(A,value=value))

    def test_fake_citation_flagged(self):
        r=self.result(a=dict(A,source_ids=['FAKE']))
        self.assertIn('MISSING_OR_UNKNOWN_CITATION_ID',r['findings'])

    def test_expected_abstention(self):
        c=dict(C,kind='abstain',expected_value=None,expected_unit=None)
        a=dict(A,abstain=True,value=None,unit=None)
        self.assertTrue(self.result(c,a)['checks']['task_result'])
        self.assertFalse(self.result(c,A)['checks']['task_result'])

    def test_zero_reference(self):
        self.assertTrue(self.result(dict(C,expected_value=0),dict(A,value=0))['checks']['task_result'])

    def test_structural_pass_still_needs_human(self):
        # An incorrect rationale with a valid number can pass the narrow checks.
        r=self.result(a=dict(A,reasoning='This unsupported statement is deliberately wrong.'))
        self.assertTrue(r['all_structural_checks_pass'])
        self.assertTrue(r['human_review_required'])

    def test_empty_reasoning(self):
        self.assertFalse(self.result(a=dict(A,reasoning='  '))['checks']['reasoning_present'])

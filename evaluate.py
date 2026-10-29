"""Deterministic checks for structured engineering answers; human review stays mandatory."""
import argparse
import json
import math
import sys
from auditlib import number, unique, evidence, cell, write_reports

# Map unit to (dimension, multiplier into canonical SI unit).
UNITS = {'m3/s':('flow',1),'L/s':('flow',0.001),'m3':('volume',1),
         'm2':('area',1),'ha':('area',10000),'m':('length',1),'mm':('length',0.001)}
CASE_FIELDS = {'id','split','prompt','kind','expected_value','expected_unit','abs_tolerance','rel_tolerance','allowed_source_ids','reference_reasoning'}
ANSWER_FIELDS = {'id','value','unit','abstain','source_ids','reasoning'}


def read_jsonl(path, fields, allow_empty=False):
    rows=[]
    with open(path,encoding='utf-8') as stream:
        for line,raw in enumerate(stream,1):
            if not raw.strip():
                continue
            try:
                obj=json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f'line {line}: invalid JSON') from exc
            if not isinstance(obj,dict) or set(obj)!=fields:
                raise ValueError(f'line {line}: fields must be exactly {sorted(fields)}')
            if not isinstance(obj['id'],str) or not obj['id'].strip():
                raise ValueError(f'line {line}: id must be a non-empty string')
            rows.append(obj)
    if not rows and not allow_empty:
        raise ValueError('case file is empty')
    unique(rows,['id'])
    return rows


def string_list(value, label):
    if not isinstance(value,list) or any(not isinstance(x,str) or not x for x in value):
        raise ValueError(f'{label}: expected a list of non-empty strings')
    if len(value)!=len(set(value)):
        raise ValueError(f'{label}: duplicate entries')


def validate_case(c):
    if not isinstance(c['kind'], str) or not isinstance(c['split'], str) or c['kind'] not in ['numeric','abstain'] or c['split'] not in ['development','holdout']:
        raise ValueError('invalid case kind or split')
    for name in ['prompt','reference_reasoning']:
        if not isinstance(c[name],str) or not c[name].strip():
            raise ValueError(f'{name} must be non-empty text')
    string_list(c['allowed_source_ids'],'allowed_source_ids')
    if not c['allowed_source_ids']:
        raise ValueError('each case must have an allowed source ID')
    number(c['abs_tolerance'],'abs_tolerance',minimum=0)
    number(c['rel_tolerance'],'rel_tolerance',minimum=0)
    if c['kind']=='numeric':
        number(c['expected_value'],'expected_value')
        if not isinstance(c['expected_unit'], str) or c['expected_unit'] not in UNITS:
            raise ValueError('unsupported expected unit')
    elif c['expected_value'] is not None or c['expected_unit'] is not None:
        raise ValueError('abstention cases require null expected value and unit')


def validate_answer(a):
    if type(a['abstain']) is not bool:
        raise ValueError('abstain must be a JSON boolean')
    if a['value'] is not None:
        number(a['value'],'answer value')
    if a['unit'] is not None and not isinstance(a['unit'],str):
        raise ValueError('unit must be text or null')
    if not isinstance(a['reasoning'],str):
        raise ValueError('reasoning must be text')
    string_list(a['source_ids'],'source_ids')


def evaluate(cases, answers):
    if not cases:
        raise ValueError('at least one case is required')
    unique(cases,['id']); unique(answers,['id'])
    for c in cases:
        validate_case(c)
    for a in answers:
        validate_answer(a)
    lookup={a['id']:a for a in answers}
    unknown=set(lookup)-{c['id'] for c in cases}
    if unknown:
        raise ValueError('unknown answer IDs: '+', '.join(sorted(unknown)))
    results=[]
    for c in cases:
        a=lookup.get(c['id'])
        checks={'task_result':False,'citation_ids':False,'reasoning_present':False}
        flags=[]
        converted=None
        if a is None:
            flags.append('MISSING_ANSWER')
        else:
            checks['citation_ids']=bool(a['source_ids']) and set(a['source_ids']).issubset(c['allowed_source_ids'])
            checks['reasoning_present']=bool(a['reasoning'].strip())
            if c['kind']=='abstain':
                checks['task_result']=a['abstain'] and a['value'] is None and a['unit'] is None
                if not checks['task_result']:
                    flags.append('UNSUPPORTED_RESULT_ON_INSUFFICIENT_INFORMATION')
            elif a['abstain']:
                flags.append('UNNECESSARY_ABSTENTION')
            elif a['value'] is None or a['unit'] not in UNITS:
                flags.append('MISSING_VALUE_OR_UNSUPPORTED_UNIT')
            else:
                dim,factor=UNITS[a['unit']]
                expected_dim,expected_factor=UNITS[c['expected_unit']]
                if dim!=expected_dim:
                    flags.append('UNIT_DIMENSION_MISMATCH')
                else:
                    converted=number(a['value'],'value')*factor/expected_factor
                    number(converted,'converted value')
                    tolerance=max(float(c['abs_tolerance']),abs(float(c['expected_value']))*float(c['rel_tolerance']))
                    error=abs(converted-float(c['expected_value']))
                    checks['task_result']=error<=tolerance or math.isclose(error,tolerance,rel_tol=1e-12,abs_tol=1e-12)
                    if not checks['task_result']:
                        flags.append('NUMERIC_ERROR')
            if not checks['citation_ids']:
                flags.append('MISSING_OR_UNKNOWN_CITATION_ID')
            if not checks['reasoning_present']:
                flags.append('EMPTY_REASONING')
        results.append({'id':c['id'],'split':c['split'],'kind':c['kind'],'checks':checks,
                        'all_structural_checks_pass':all(checks.values()),'converted_value':converted,
                        'expected_unit':c['expected_unit'],'findings':flags,'human_review_required':True})
    summary={}
    for split in ['all','development','holdout']:
        group=[r for r in results if split=='all' or r['split']==split]
        n=len(group)
        summary[split]={'cases':n,'answers_present':sum('MISSING_ANSWER' not in r['findings'] for r in group),
                        'task_result_passes':sum(r['checks']['task_result'] for r in group),
                        'all_structural_passes':sum(r['all_structural_checks_pass'] for r in group),
                        'structural_pass_rate':sum(r['all_structural_checks_pass'] for r in group)/n if n else None}
    return {'demo':True,'method':'structured-answer-checks-v1','summary':summary,'results':results,
            'warning':'Synthetic fixture results, not model performance. Citation IDs do not establish source entailment. All answers need human review.'}


def render(report):
    lines=['# Engineering answer evaluation','','**Synthetic fixture — not a benchmark of a model.**','',
           '| Split | Cases | Answers present | Task result passes | All structural checks pass |',
           '|---|---:|---:|---:|---:|']
    for split,s in report['summary'].items():
        lines.append(f"| {split} | {s['cases']} | {s['answers_present']} | {s['task_result_passes']} | {s['all_structural_passes']} |")
    lines+=['','| Case | Result | Findings | Human review |','|---|---|---|---|']
    for r in report['results']:
        lines.append(f"| {cell(r['id'])} | {'Structural checks pass' if r['all_structural_checks_pass'] else 'Needs correction'} | {', '.join(r['findings']) or 'None detected by these checks'} | Required |")
    lines+=['','Citation matching checks identifiers only; it does not validate whether a source supports the answer. Reasoning is checked for presence, not correctness.','']
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('cases'); p.add_argument('answers')
    p.add_argument('--out',default='reports')
    p.add_argument('--fail-on-findings',action='store_true')
    a=p.parse_args()
    try:
        cases=read_jsonl(a.cases,CASE_FIELDS)
        answers=read_jsonl(a.answers,ANSWER_FIELDS,allow_empty=True)
        report=evaluate(cases,answers)
        report['inputs']=evidence([a.cases,a.answers])
        write_reports(a.out,report,render(report))
    except (ValueError,OSError,OverflowError) as exc:
        print(f'Input/report error: {exc}',file=sys.stderr)
        return 2
    s=report['summary']['all']
    print(f"{s['all_structural_passes']}/{s['cases']} pass structural checks. Human review required for every answer. Reports: {a.out}")
    return int(a.fail_on_findings and s['all_structural_passes'] < s['cases'])


if __name__=='__main__':
    sys.exit(main())

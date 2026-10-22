"""Reconcile the two blind DOI-verification runs against the claimed bibliographic record.

Run A (Crossref + doi.org handle) and Run B (OpenAlex + Semantic Scholar + DataCite) never saw the
claimed metadata or each other's output. This script is the only place the three are compared.

Inputs:  claimed.json (from build_claimed.py) = {doi: {"title":..., "year":..., "first_author":..., "venue":...}},
         runA.json (verify_run_A.py), runB.json (verify_run_B.py).
Output:  out.json {"summary": {...verdict counts, Cohen's kappa, PABAK, Gwet's AC1...}, "records": {doi: {...}}}.

Example: python -P verify_reconcile.py verify/claimed.json verify/runA.json verify/runB.json verify/reconciled.json
Requires: standard library only. Makes no network calls.
"""
import argparse
import difflib
import json
import re
import unicodedata

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('claimed'); ap.add_argument('runA'); ap.add_argument('runB'); ap.add_argument('out')
ap.add_argument('--title-ok', type=float, default=0.90, help='title similarity for a match (default: 0.90)')
ap.add_argument('--title-soft', type=float, default=0.80, help='title similarity for a minor difference (default: 0.80)')
args = ap.parse_args()

claimed, A, B = (json.load(open(p, encoding='utf-8')) for p in (args.claimed, args.runA, args.runB))
out_path = args.out

TITLE_OK = args.title_ok      # normalised similarity needed for a title match
TITLE_SOFT = args.title_soft  # between SOFT and OK -> "minor" (punctuation, subtitle, Greek letters)


def norm(s):
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode()
    s = re.sub(r'<[^>]+>', ' ', s).lower()
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def tsim(a, b):
    a, b = norm(a), norm(b)
    if not a or not b:
        return None
    r = difflib.SequenceMatcher(None, a, b).ratio()
    short, long_ = sorted((a, b), key=len)
    if len(short) > 25 and long_.startswith(short):   # subtitle dropped by one index
        r = max(r, 0.97)
    return round(r, 3)


AFFIL = re.compile(r'universit|department|faculty|institut|college|school|laborator|centre|center')


def amatch(a, b):
    """Token-based first-author check. Returns None when either side is missing or is an
    affiliation string that Crossref sometimes stores in the author field."""
    a, b = norm(a), norm(b)
    if not a or not b or AFFIL.search(a) or AFFIL.search(b):
        return None
    ta = {t for t in a.split() if len(t) >= 2}
    tb = {t for t in b.split() if len(t) >= 2}
    if not ta or not tb:          # initials only, e.g. "V" or "J."
        return None
    if ta & tb:
        return True
    return any(x[:4] == y[:4] for x in ta for y in tb if len(x) >= 4 and len(y) >= 4)


def ymatch(c, *ys):
    ys = [int(y) for y in ys if y]
    if not c or not ys:
        return None
    return any(abs(int(c) - y) <= 1 for y in ys)


rows, n_pair, n_agree = {}, 0, 0
a_flags, b_flags = [], []
for d, c in claimed.items():
    a, b = A.get(d, {}), B.get(d, {})
    r = {'doi': d, 'claimed_title': c.get('title'), 'claimed_year': c.get('year'),
         'claimed_first_author': c.get('first_author'),
         'handle_exists': a.get('handle_exists'), 'resolves_to': a.get('resolves_to')}
    # per-source agreement with the claimed record
    srcs = {}
    if a.get('cr_found'):
        t = a.get('cr_title') or ''
        if a.get('cr_subtitle'):
            t2 = t + ' ' + a['cr_subtitle']
            ts = max(tsim(c.get('title'), t) or 0, tsim(c.get('title'), t2) or 0)
        else:
            ts = tsim(c.get('title'), t)
        srcs['crossref'] = {'title_sim': ts, 'year_ok': ymatch(c.get('year'), a.get('cr_year_issued'), a.get('cr_year_print'), a.get('cr_year_online')),
                            'author_ok': amatch(c.get('first_author'), a.get('cr_first_author')), 'title': t,
                            'year': a.get('cr_year_issued'), 'first_author': a.get('cr_first_author'), 'venue': a.get('cr_container')}
    if b.get('oa_found'):
        srcs['openalex'] = {'title_sim': tsim(c.get('title'), b.get('oa_title')), 'year_ok': ymatch(c.get('year'), b.get('oa_year')),
                            'author_ok': amatch(c.get('first_author'), b.get('oa_first_author')), 'title': b.get('oa_title'),
                            'year': b.get('oa_year'), 'first_author': b.get('oa_first_author'), 'venue': b.get('oa_venue')}
    if b.get('s2_found'):
        srcs['semanticscholar'] = {'title_sim': tsim(c.get('title'), b.get('s2_title')), 'year_ok': ymatch(c.get('year'), b.get('s2_year')),
                                   'author_ok': amatch(c.get('first_author'), b.get('s2_first_author')), 'title': b.get('s2_title'),
                                   'year': b.get('s2_year'), 'first_author': b.get('s2_first_author'), 'venue': b.get('s2_venue')}
    if b.get('dc_found'):
        srcs['datacite'] = {'title_sim': tsim(c.get('title'), b.get('dc_title')), 'year_ok': ymatch(c.get('year'), b.get('dc_year')),
                            'author_ok': amatch(c.get('first_author'), b.get('dc_first_author')), 'title': b.get('dc_title'),
                            'year': b.get('dc_year'), 'first_author': b.get('dc_first_author'), 'venue': None}

    def ok(s):
        return (s['title_sim'] or 0) >= TITLE_OK and s['author_ok'] is not False and s['year_ok'] is not False

    def soft(s):
        # title still agrees; author formatting or online-vs-print year may differ
        return (s['title_sim'] or 0) >= TITLE_SOFT

    matching = [k for k, s in srcs.items() if ok(s)]
    softm = [k for k, s in srcs.items() if soft(s) and k not in matching]
    contra = [k for k, s in srcs.items() if not soft(s)]   # only a title disagreement is a conflict
    # independent cross-check between the two blind runs (Crossref in A vs S2/OpenAlex in B)
    cross = None
    if a.get('cr_found') and (b.get('s2_found') or b.get('oa_found')):
        bt = b.get('s2_title') if b.get('s2_found') else b.get('oa_title')
        cross = tsim(a.get('cr_title'), bt)
        n_pair += 1
        n_agree += int((cross or 0) >= TITLE_OK)
    a_flags.append(bool(a.get('cr_found') and srcs.get('crossref') and ok(srcs['crossref'])))
    b_flags.append(any(ok(srcs[k]) for k in ('openalex', 'semanticscholar', 'datacite') if k in srcs))
    retracted = bool(a.get('cr_is_retracted_notice') or b.get('oa_is_retracted'))
    if a.get('handle_exists') is False:
        verdict = 'NOT_FOUND (DOI not registered)'
    elif contra:
        verdict = 'CONFLICT (check manually)'
    elif len(matching) >= 2 and a.get('handle_exists'):
        verdict = 'VERIFIED'
    elif len(matching) + len(softm) >= 2 and a.get('handle_exists'):
        verdict = 'VERIFIED (minor metadata differences)'
    elif len(matching) == 1 and a.get('handle_exists'):
        verdict = 'VERIFIED (single index + registry)'
    else:
        verdict = 'UNRESOLVED'
    if retracted:
        verdict += ' | RETRACTION/UPDATE NOTICE'
    r.update({'sources': srcs, 'n_sources_found': len(srcs), 'n_sources_matching': len(matching),
              'matching_sources': matching, 'minor_sources': softm, 'contradicting_sources': contra,
              'runA_vs_runB_title_similarity': cross, 'crossref_updated_by': a.get('cr_updated_by'),
              'retraction_flag': retracted, 'verdict': verdict,
              'canonical_title': (a.get('cr_title') or b.get('oa_title') or b.get('s2_title')),
              'canonical_year': a.get('cr_year_issued') or b.get('oa_year'),
              'canonical_venue': a.get('cr_container') or b.get('oa_venue'),
              'canonical_first_author': a.get('cr_first_author') or b.get('oa_first_author'),
              'cr_authors': a.get('cr_authors'), 'cr_volume': a.get('cr_volume'), 'cr_page': a.get('cr_page'),
              'cr_publisher': a.get('cr_publisher')})
    rows[d] = r

# Cohen's kappa between the two blind runs' binary "confirms the claimed record" decisions
n = len(a_flags)
po = sum(x == y for x, y in zip(a_flags, b_flags)) / n if n else 0
pa, pb = sum(a_flags) / n if n else 0, sum(b_flags) / n if n else 0
pe = pa * pb + (1 - pa) * (1 - pb)
kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
# Strictly independent pair: Crossref (run A) vs Semantic Scholar (run B); OpenAlex is excluded because
# the claimed metadata for harvested records came from OpenAlex. Only DOIs indexed by both are compared.
pairs = []
for d, r in rows.items():
    s = r['sources']
    if 'crossref' in s and 'semanticscholar' in s:
        okk = lambda x: (x['title_sim'] or 0) >= TITLE_OK and x['author_ok'] is not False and x['year_ok'] is not False
        pairs.append((okk(s['crossref']), okk(s['semanticscholar'])))
m = len(pairs)
po2 = sum(x == y for x, y in pairs) / m if m else 0
pa2 = sum(x for x, _ in pairs) / m if m else 0
pb2 = sum(y for _, y in pairs) / m if m else 0
pe2 = pa2 * pb2 + (1 - pa2) * (1 - pb2)
kappa2 = (po2 - pe2) / (1 - pe2) if pe2 < 1 else 1.0
pi = (pa2 + pb2) / 2
pe_ac1 = 2 * pi * (1 - pi)
ac1 = (po2 - pe_ac1) / (1 - pe_ac1) if pe_ac1 < 1 else 1.0
indep = {'n_pairs_crossref_s2': m, 'both_confirm': sum(x and y for x, y in pairs),
         'only_crossref': sum(x and not y for x, y in pairs), 'only_s2': sum(y and not x for x, y in pairs),
         'neither': sum((not x) and (not y) for x, y in pairs), 'observed_agreement': round(po2, 4),
         'cohens_kappa': round(kappa2, 4), 'pabak': round(2 * po2 - 1, 4), 'gwet_ac1': round(ac1, 4)}
summary = {'independent_pair_crossref_vs_semanticscholar': indep,
           'n_dois': n, 'runA_confirms': sum(a_flags), 'runB_confirms': sum(b_flags),
           'both_confirm': sum(x and y for x, y in zip(a_flags, b_flags)),
           'observed_agreement': round(po, 4), 'cohens_kappa': round(kappa, 4),
           'cross_title_pairs': n_pair, 'cross_title_agree': n_agree,
           'verdicts': {}}
for r in rows.values():
    summary['verdicts'][r['verdict']] = summary['verdicts'].get(r['verdict'], 0) + 1
json.dump({'summary': summary, 'records': rows}, open(out_path, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(summary, indent=1))

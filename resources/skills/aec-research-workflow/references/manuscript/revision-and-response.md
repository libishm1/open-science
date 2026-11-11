# Revision after peer review: tracked changes, response letters and the editor

From Project C's first-round revision (three reviewers and an editor; accepted after one round). The science
held; what took the work was keeping the manuscript, three response letters and a cover letter consistent
through five rebuilds.

## 1. Triage before touching anything

- Read every report, the editor's message and the review form (ticks such as "English is fine").
- Classify each reviewer as minor, moderate or major **by workload** and separately **by risk**. Supportive tone
  ("commendable", "somewhat novel") with many requests is major work and low risk. Say when the official
  decision category is not visible.
- When the supervisor asks "is it major?", answer in one line per reviewer and one line overall, then the plan.
- Number every comment and extract it verbatim before changing anything ([reviewer-comment-patterns.md](reviewer-comment-patterns.md), "Working the round").

## 2. Edit the publisher's formatted DOCX, with real tracked changes

After the first round the journal may supply its formatted DOCX with line numbers, and the reviewers quote those
line numbers. Rebuilding from your own source loses both. Edit that file with Word revisions (`w:ins`/`w:del`)
so the editor can accept or reject each one, and produce the clean copy by accepting all
([`scripts/track_changes.py`](../../scripts/track_changes.py)).

- Pass whole sentences: the diff is token-level, so only the changed words are marked.
- Later edits cannot anchor on text an earlier edit inserted, because the editable text excludes tracked runs.
  A rewrite once removed the anchor of a later edit; the paragraph assert reported 0 matches. Re-anchor on
  untouched words; never loosen the assert.
- Order the passes: content edits, then global passes (readability), then **citation renumbering last**.
  Renumbering rewrites numbers in untouched text, while inserted text is written with the new numbers.
- A citation added early (for example in the Introduction) renumbers a numbered-citation paper by first
  appearance: move the reference entry as a tracked deletion and insertion, and re-check the order.
- Replace figures in `word/media` at the pixel size of the embedded image, set the revision author to the
  corresponding author, and export both versions to PDF and read them.

## 3. One source for every changed sentence

Every new or rewritten sentence lives once, in a strings module that both the manuscript editor and the letter
builder import. The letter's "Change (Section 4.4, line 663): '...'" then quotes exactly what the manuscript
says. When a later reviewer's change rewrites a sentence first added for an earlier reviewer, edit the one
string, and let the earlier letter follow.

Verify anyway: `revision_checks.py quotes CLEAN.docx letters...` checks every quoted fragment against the clean
manuscript (fragments split at "...", and for '"old" -> "new"' only the new text). After a readability pass it
found three stale quotes, one of which was older than the pass.

## 4. The response letter

- Per reviewer: comment verbatim, response, then "Change (location): 'quoted new text'". Locations give the
  section and the line numbers of the version the reviewers read.
- Agree where the reviewer is right; adopt the reviewer's own phrasing for a narrowed conclusion.
- Decline in one sentence with the reason (a recommended reference unrelated to the content; editors often allow
  this explicitly). Never decline silently.
- **No response-only exhibits that were not requested.** A table or figure that appears only in the letter
  invites "please add this to the manuscript". Give the numbers in the text; keep only the exhibit the reviewer
  asked for. (Project C dropped three of four at the supervisor's request; the requested curve stayed.)
- The cover letter answers the editor's points in the editor's numbering, states how many new simulations were
  run, and names the new supplementary files.

## 5. New analyses requested in review

Additive, reproducing the frozen numbers first, with **the prediction written into the run script before the
runs** so that no result can be retrofitted. Report a failed prediction as plainly as a confirmed one.

| Request | The check that answered it |
|---|---|
| Case-months are not independent samples | Grouped cross-validation: leave one case out and one city out, next to leave-one-out; report all three |
| Why this threshold and this bin width | Re-run at alternative thresholds and widths; state which conclusions hold in every combination |
| Is the attributed share latent, or control timing | Inert-layer controls under the same control. When inert layers switched differently (20 to 53% more open hours), the share was renamed "the contribution of the PCM and its interaction with the control" |
| Is the minimum temperature enough | A duration indicator (degree-hours below the threshold) and a physical upper bound from the wall conductance |
| What if the microclimate is off by 2 K | Simulate the shifted weather directly (full shift in the night window, linear tapers either side, dew point capped, sky infrared scaled with T^4) instead of re-classifying |
| Is hourly output hiding cycles | Re-run with per-time-step output and compare with the hourly census |
| Is the upper limit general | One level beyond the tested range at the second setpoint |

Each check narrowed at least one claim ("every layer that cycled increased cooling" held only for fortnight
cycles against annual savings). Narrow; do not defend. Ship the scripts and results as a separate checks zip,
named in the Supplementary Materials and Data Availability statements, with no personal paths.

## 6. Manufacturer data sheets as a source

- A data sheet's "heat storage capacity" (160 to 250 kJ/kg for one paraffin range) combines latent and sensible
  heat over about 15 K. Read the definition printed on the sheet before calling it latent heat.
- Vendor sites restructure: retrieve the sheets from the Internet Archive (`id_` captures keep the original
  bytes), record each capture URL in a `SOURCES.md`, and cite the archived URL with its access date.
- One reference per sheet: production will ask for it anyway (see [publisher-proofs.md](publisher-proofs.md)).
- Compare the sheets with the model's assumptions (a 2 K hysteresis against sheets showing 0 to 1 K) and flag
  the difference to the author even when no reviewer raised it.

## 7. "More straightforward grammar" from the editor

When every reviewer ticks "English is fine" and the editor still asks for straighter grammar, the problem is
sentence length. Measure it (`revision_checks.py readability`): Project C had a median of 30 words and 70
sentences over 50 words, many of them added in the revision itself.

- Split at semicolons, colon lists and long parenthetical qualifications; give the revision's own text the same
  treatment. Keep content and numbers unchanged.
- Prove the pass was content-neutral: `numbers OLD NEW` (multiset of numbers unchanged), `order` (citations and
  first table and figure mentions still ascending), `typography`, and `quotes` again.
- Answer the editor with one paragraph in the cover letter and a two- or three-sentence version for the portal.

## 8. Before uploading

```
[ ] tracked and clean DOCX + PDF built from the publisher's file; every page read
[ ] revision_checks.py quotes / numbers / order / typography pass
[ ] each comment answered in the reviewer's numbering; declines carry a reason
[ ] no response-only exhibit that was not requested
[ ] new analyses: predictions dated before the runs; checks zip has no personal paths
[ ] cover letter: editor's points in order, count of new simulations, new files named
[ ] one zip, a short message for the supervisor, open decisions listed
```

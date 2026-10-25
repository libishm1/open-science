# Phase 5: Quality Control

Part of the academic-paper-composer skill. Load only this file for this topic.

### Goal
Perform comprehensive final evaluation and prepare submission-ready manuscript.

### Workflow

#### Step 5.1: Content Completeness Check

Using structured checklist, verify:

**Structural Completeness**:
- [ ] Abstract (250-300 words)
- [ ] Introduction with all required elements
- [ ] All outlined main chapters present
- [ ] Conclusion with all required elements
- [ ] References section formatted correctly

**Content Completeness**:
- [ ] All introduction promises fulfilled
- [ ] All claims supported by evidence or argument
- [ ] All technical terms defined
- [ ] All objections addressed
- [ ] All limitations acknowledged

**Citation Completeness**:
- [ ] Every citation in text has bibliography entry
- [ ] Every bibliography entry cited in text
- [ ] Citation format consistent throughout
- [ ] All citations include necessary information

**Format Completeness**:
- [ ] Title page (if required)
- [ ] Section numbering consistent
- [ ] Heading hierarchy logical
- [ ] Figure/table captions (if applicable)

**Output**: Completeness checklist report

#### Step 5.2: Final 7-Dimension Evaluation

I will perform comprehensive evaluation using:

```bash
python scripts/final_evaluation.py
# Create evaluation template
```

**7 Dimensions** (10 points each, 70 total):

1. **Overall Argument Quality** (1-10)
   - Thesis clarity throughout
   - Chapter integration
   - Logical completeness
   - Objections addressed

2. **Literature Integration** (1-10)
   - Citation count (40-60 typical for philosophy)
   - Key literature covered
   - Citations well-integrated
   - Critical engagement present

3. **Clarity & Accessibility** (1-10)
   - Prose clarity
   - Complex ideas explained
   - Appropriate for audience
   - Technical terms defined

4. **Originality & Contribution** (1-10)
   - Clear original contribution
   - Advance over literature
   - Significance established
   - Innovation present

5. **Methodological Rigor** (1-10)
   - Method explicit and justified
   - Consistently applied
   - Appropriate for question
   - Limitations acknowledged

6. **Structure & Organization** (1-10)
   - Logical flow
   - Optimal organization
   - Proportions balanced
   - Transitions seamless

7. **Platform & Style Conformity** (1-10)
   - Style matches platform
   - Format correct
   - Voice consistent
   - Citation format perfect

**Scoring Process**:
1. Evaluate each dimension (1-10)
2. Provide detailed notes for each
3. Complete completeness checklist
4. List any specific issues

**Generate report**:
```bash
python scripts/final_evaluation.py
# Generate final report
```

This produces:
- Total score (X/70)
- Pass/fail (threshold: ≥56/70)
- Weak dimensions identified
- Completeness assessment
- Prioritized revision recommendations
- Submission readiness decision

**Quality Gate 5** (Final):
- ✓ Score ≥56/70 (80%)
- ✓ All completeness checklist items complete
- ✓ All high-priority issues addressed

**If Failed**: Implement revisions and re-evaluate

#### Step 5.3: Revision Implementation (If Needed)

If final score <56/70 or completeness incomplete:

1. **Prioritize revisions**:
   - HIGH priority: All issues affecting score or completeness
   - MEDIUM priority: Issues improving quality
   - LOW priority: Optional enhancements

2. **Implement systematically**:
   - Address high-priority first
   - Document changes
   - Maintain style consistency

3. **Re-evaluate**:
   - Generate new final report
   - Verify score ≥56/70
   - Check completeness 100%

4. **Iterate until passing**

**Decision Point 3**: After final evaluation, I will:
- Present final score and assessment
- Show submission readiness status
- Recommend: Submit immediately / Implement optional improvements / Required revisions
- Ask: Proceed with submission or implement further improvements?

#### Step 5.4: Submission Package Preparation

Once final evaluation passes:

1. **Platform-specific checklist**:
   - **PhilArchive/PhilPapers**:
     - [ ] PDF format
     - [ ] Abstract <500 words
     - [ ] Metadata (title, keywords, classification)
     - [ ] Author information complete

   - **arXiv**:
     - [ ] LaTeX or PDF format
     - [ ] Abstract <1920 characters
     - [ ] Category selection correct
     - [ ] No font embedding issues

   - **PhilSci-Archive**:
     - [ ] PDF format
     - [ ] Subject classification
     - [ ] Keywords (3-5)
     - [ ] No copyright issues

2. **Generate final outputs**:
   - Formatted manuscript (PDF or LaTeX)
   - Abstract (separate file if needed)
   - Metadata file
   - Cover letter (if applicable)

3. **Pre-submission verification**:
   - Re-read complete paper
   - Check all formatting
   - Verify all links/citations work
   - Proofread for typos

**Output**: Complete submission package ready for platform upload

---

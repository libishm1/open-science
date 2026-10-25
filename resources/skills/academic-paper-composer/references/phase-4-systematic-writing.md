# Phase 4: Systematic Writing

Part of the academic-paper-composer skill. Load only this file for this topic.

### Goal
Write complete manuscript chapter-by-chapter with iterative quality control.

### Workflow

#### Step 4.1: Writing Environment Setup

Before writing, I will:

1. **Verify outline completeness**:
   - All chapters specified with word counts
   - Content guidance provided
   - Argument structure clear

2. **Load reference documents**:
   - Platform writing standards
   - Section writing guides (`references/section_guides.md`)
   - Quality standards (`references/writing_standards.md`)

3. **Create writing tracker**:
   ```markdown
   # Writing Progress Tracker
   - [ ] Abstract (250 words)
   - [ ] Chapter 1: Introduction (1,500 words)
   - [ ] Chapter 2: [Title] (1,200 words)
   ...
   - [ ] Conclusion (1,000 words)
   - [ ] References
   ```

**Decision Point 1**: Confirm outline and standards loaded, ready to begin writing.

#### Step 4.2: Chapter-by-Chapter Writing

**For each chapter, I will follow this sequence**:

##### A. Pre-Writing Review
Before writing chapter N:
1. **Review outline specification** for this chapter:
   - Word count target
   - Subsection structure
   - Content guidance
   - Key arguments/citations

2. **Review previous chapter** (if N>1):
   - Last paragraph of chapter N-1
   - Key concepts introduced
   - Promises to fulfill

3. **Check section guide**:
   - Load appropriate template from `references/section_guides.md`
   - Review quality markers for this section type

##### B. Writing Execution

I will write the chapter following:

**Content principles**:
- **Follow outline exactly**: Respect structure and word counts
- **Include specified citations**: Use literature from outline
- **Maintain platform style**: Match voice and terminology
- **Use section templates**: Follow appropriate guide from `section_guides.md`

**Quality targets (pre-emptive)**:
- Argument quality: Clear thesis, justified premises
- Citation quality: All claims supported, proper format
- Clarity: Precise prose, terms defined, good transitions
- Structure: Logical flow, proper proportions
- Style conformity: Match platform conventions

**Output**: Complete chapter draft

##### C. Post-Writing Evaluation

After completing chapter draft, I will:

1. **Create evaluation document**:
   ```bash
   python scripts/chapter_quality_check.py
   # Option 1: Create template for this chapter
   ```

2. **Perform 5-dimension assessment**:
   - **Argument Quality** (1-4): Thesis clear? Premises justified? Objections addressed?
   - **Citation Quality** (1-4): All claims cited? Format consistent? Key literature included?
   - **Clarity & Readability** (1-4): Prose clear? Terms defined? Transitions smooth?
   - **Structure & Flow** (1-4): Logical progression? Proper proportions? Follows outline?
   - **Platform Conformity** (1-4): Style match? Voice consistent? Format correct?

3. **Generate quality report**:
   ```bash
   python scripts/chapter_quality_check.py
   # Option 2: Generate report from evaluation
   ```

   This produces:
   - Total score (X/20)
   - Pass/fail (threshold: ≥16/20)
   - Weak dimensions identified
   - Specific revision recommendations

**Quality Gate 4A** (After Each Chapter):
- ✓ Score ≥16/20 (80%)
- ✓ All dimensions ≥3/4 (or revisions implemented)
- ✓ Word count within ±10% of target

**If Failed**: Implement revisions before proceeding to next chapter

##### D. Iteration (If Needed)

If chapter scores <16/20:

1. **Identify weak dimension(s)**: Which scored <3/4?

2. **Implement targeted revisions**:
   - Argument quality issue → Add justifications, address objections
   - Citation quality issue → Add supporting citations, fix format
   - Clarity issue → Simplify prose, add definitions, improve transitions
   - Structure issue → Reorganize paragraphs, adjust proportions
   - Style issue → Adjust voice, terminology, format

3. **Re-evaluate**: Generate new quality report

4. **Repeat until passing** (typically 1-2 iterations)

**Important**: Do not proceed to next chapter until current chapter passes quality gate.

##### E. Chapter Completion

Once chapter passes quality gate:

1. **Mark chapter complete** in writing tracker
2. **Save chapter with quality report**
3. **Note key concepts introduced** (for coherence check later)
4. **Preview next chapter** requirements

**Decision Point 2** (After Major Chapters): After completing each main body chapter, I will:
- Present completed chapter summary
- Show quality score
- Ask: Proceed to next chapter or revise further?

#### Step 4.3: Writing Sequence

**Recommended order**:

1. **Introduction** (write first)
   - Establishes thesis and roadmap
   - Use introduction guide from `section_guides.md`
   - Quality check: Abstract promises, literature coverage, clear contribution

2. **Main Body Chapters** (in outline order)
   - Follow outline sequence
   - Quality check after each
   - Build on previous chapters

3. **Conclusion** (write after main body)
   - Synthesizes findings
   - Addresses introduction promises
   - Use conclusion guide from `section_guides.md`

4. **Abstract** (write last)
   - Summarizes complete paper
   - Use abstract guide from `section_guides.md`
   - Quality check: Standalone, accurate, compelling

5. **References** (compile throughout)
   - Format according to platform standards
   - Verify all citations present

#### Step 4.4: Cross-Chapter Coherence Check

After all chapters written, before final evaluation:

1. **Terminology consistency**:
   - Extract key terms from each chapter
   - Verify consistent usage throughout
   - Check definitions consistent

2. **Argument flow**:
   - Verify chapter N+1 builds on chapter N
   - Check roadmap (intro) matches execution
   - Ensure conclusion addresses introduction promises

3. **Citation patterns**:
   - Check for uneven citation distribution
   - Verify key works cited where relevant
   - Ensure bibliography complete

**Output**: Cross-chapter coherence report identifying any inconsistencies

---

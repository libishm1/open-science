# Phase 2: Theoretical Framework

Part of the academic-paper-strategist skill. Load only this file for this topic.

### Goal
AI-driven systematic literature search, research gap identification, and originality assessment.

### Input Required from User
- **Core research question/thesis** (your main argument)
- **Background context** (why you're interested in this)
- **Optional**: Any papers you already know about

### Workflow

#### Step 2.1: Literature Search (AI-Driven, Fully Automated)

**Important**: This phase is **AI-driven**. You provide your idea; I conduct comprehensive literature search and gap analysis.

**Multi-Round Search Strategy**:

**Round 1: Direct Search (Primary Literature)**
1. **Extract core concepts** from your idea (3-5 concepts)
2. **Generate keyword combinations** (10-15 combinations)
   - Concept + concept
   - Concept + method
   - Include synonyms and disciplinary variants
3. **Search each combination** using Exa/Tavily
4. **Collect 30-50 candidate papers**
5. **Quality filter**: Retain top 20 papers (relevance ≥7/10)

**Round 2: Expanded Search (Adjacent Fields)**
1. **Extract new keywords** from Round 1 papers
2. **Search adjacent disciplines**:
   - Philosophy → cognitive science
   - Neuroscience → philosophy of mind
   - AI → consciousness studies
3. **Collect 10-20 bridging papers**

**Round 3: Classic Literature (Foundational Works)**
1. **Identify highly-cited papers** (>100 citations)
2. **Track citations** from Round 1-2 papers
3. **Collect 5-10 foundational papers**

**Total Literature Base**: 35-50 papers

**Load Reference**: `references/search_strategy.md` for detailed methodology

#### Step 2.2: Research Gap Identification (AI Analysis)

Using collected literature, I will **automatically identify** 3-5 research gaps:

**Gap Identification Methods**:

1. **Concept Mapping**:
   - Plot papers on Concept × Method matrix
   - Identify white spaces (unexplored combinations)

2. **Problem-Solution Analysis**:
   - What problems does literature address?
   - What limitations do authors acknowledge?
   - What questions remain unanswered?

3. **Temporal Analysis**:
   - What was once studied but abandoned?
   - What emerged recently but unexplored?

**Gap Types**:
- **Complete gaps**: No existing research
- **Partial gaps**: Preliminary work only, needs development
- **Controversy gaps**: Competing theories, no resolution

**For Each Gap, I Document**:
- Clear definition (50-100 words)
- Evidence (3-5 citations showing gap exists)
- Significance assessment (High/Medium/Low)
- Feasibility assessment (Can you address it?)

**Validation**: Run `scripts/gap_analysis.py` to ensure quality:
```bash
python scripts/gap_analysis.py
```

This validates:
- Each gap has ≥3 pieces of evidence
- Definitions are specific and clear
- Significance is justified

**Quality Gate 2** (Must Pass):
- ✓ Literature base ≥20 papers
- ✓ Identified gaps ≥3
- ✓ Each gap has ≥3 evidence citations
- ✓ At least 1 high-significance gap

**If Failed**: Continue search or pivot research direction

**Output**: `Literature_Review_Report.md` + `Research_Gap_Analysis.md`

#### Step 2.3: Originality Assessment (AI Analysis)

I will **automatically assess** your idea's originality:

**Step 1: Similarity Analysis**
- Compare your idea with top 15 most similar papers
- Create similarity matrix (topic/method/conclusion overlap)
- Calculate overall similarity percentage

**Interpretation**:
- >80%: High similarity, needs repositioning
- 50-80%: Moderate, emphasize differences
- <50%: Good originality, proceed

**Step 2: Innovation Classification**

Identify which innovation types apply (need ≥2):
1. **Methodological**: New approach to known problem
2. **Theoretical**: New framework or model
3. **Application**: Existing theory to new domain
4. **Integrative**: Synthesizing separate literatures

**Step 3: Impact Prediction (1-10 scale)**

**Scoring Criteria**:
- **Gap Importance** (5 points): Core vs. peripheral problem?
- **Generalizability** (3 points): Widely applicable?
- **Explanatory Power** (2 points): Resolves existing puzzles?

**Target**: ≥7/10 for good impact potential

**Output**: `Originality_Assessment_Report.md` (similarity analysis + innovation types + impact prediction + 300-word justification)

#### Step 2.4: Core Concepts Discussion (Interactive)

**Decision Point 2**: Based on literature analysis, I will:

1. **Propose 3-5 core concepts** to emphasize
2. **Explain rationale** (based on gap analysis + literature frequency)
3. **Ask for your feedback**: Agree? Adjust? Add?

This ensures the paper focuses on the right concepts to maximize contribution.

---

# Phase 1: Platform Analysis

Part of the academic-paper-strategist skill. Load only this file for this topic.

### Goal
Identify the optimal submission platform and understand its writing standards through systematic sample paper analysis.

### Input Required from User
- **Core research idea or topic** (brief description)
- **Target platform** (optional - if unclear, I'll recommend)
- **Field/discipline** (philosophy, cognitive science, interdisciplinary, etc.)

### Workflow

#### Step 1.1: Platform Selection (If Needed)

If target platform unclear, I will:

1. **List candidate platforms** based on research content:
   - **PhilArchive/PhilPapers**: Philosophy papers, phenomenology, metaphysics
   - **arXiv (cs.AI, q-bio.NC)**: Computational, neuroscience, AI-related
   - **PhilSci-Archive**: Philosophy of science, formal methods
   - **PsyArXiv**: Psychology, cognitive science
   - **SocArXiv**: Social sciences, interdisciplinary

2. **Evaluate each platform**:
   - Subject area alignment (does your topic fit?)
   - Methodology match (philosophical/empirical/computational)
   - Acceptance criteria
   - Typical review timeline

3. **Provide recommendation** with reasoning

4. **Decision Point 1**: You confirm platform or suggest alternative

#### Step 1.2: Sample Paper Search (AI-Driven, Quality-Controlled)

I will conduct **multi-dimensional search** for 8-10 representative papers:

**Search Strategy** (load `references/search_strategy.md` for details):

**Time Dimension**:
- Recent (last 6 months): 3 papers - capture current trends
- Current (1-2 years): 3 papers - established standards
- Classic (highly cited): 2 papers - quality benchmarks

**Relevance Dimension**:
- Use keyword combinations from your topic
- Score each paper 0-10 for relevance
- Retain only papers scoring ≥7/10

**Diversity Dimension**:
- Multiple authors (≥5 unique)
- Different research perspectives
- Varied paper lengths

**Tools Used**:
- Exa MCP (semantic search)
- Tavily MCP (web search)
- Platform-specific search (PhilPapers, arXiv)

**Quality Validation**:
After search, I'll run `scripts/evaluate_samples.py` to generate evaluation report:
```bash
python scripts/evaluate_samples.py
```

This produces:
- Sample quality metrics
- Time distribution check
- Relevance statistics
- Diversity assessment
- Pass/Fail recommendation

**Quality Gate 1** (Must Pass):
- ✓ Sample papers ≥8
- ✓ Time distribution balanced
- ✓ Average relevance ≥8/10
- ✓ Unique authors ≥5

**If Failed**: Re-search with adjusted criteria

#### Step 1.3: Writing Standards Extraction

From the 8-10 sample papers, I will extract:

**Structural Patterns**:
- Abstract structure (Problem→Method→Results→Contribution?)
- Chapter organization (how many sections? typical flow?)
- Average proportions (Intro 15%, Main 70%, Conclusion 15%?)

**Style Patterns**:
- First-person vs passive voice usage
- How arguments are structured
- Citation density and format
- Use of technical terminology

**Format Specifications**:
- Typical word count range
- Reference count range
- Section heading conventions

**Output**: `[Platform]_Writing_Standards_Guide.md`

---

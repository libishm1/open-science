# Quality Assurance System

Part of the academic-paper-strategist skill. Load only this file for this topic.

### Quality Standards Reference

For detailed evaluation criteria, load:
```markdown
references/quality_standards.md
```

This document defines:
- Sample paper selection criteria
- Literature search comprehensiveness metrics
- Gap identification requirements
- Reviewer assessment rubrics
- Quality gate thresholds

### Evaluation Scripts

Two Python scripts support quality validation:

#### 1. Sample Paper Evaluator
```bash
python scripts/evaluate_samples.py
```

**Function**: Validates collected sample papers against quality standards
- Checks time distribution
- Calculates average relevance
- Verifies diversity
- Generates evaluation report

**When to Use**: After Step 1.2 (sample paper search)

#### 2. Gap Analysis Validator
```bash
python scripts/gap_analysis.py
```

**Function**: Validates identified research gaps
- Checks evidence sufficiency (≥3 per gap)
- Validates gap definitions
- Assesses significance justifications
- Generates gap portfolio report

**When to Use**: After Step 2.2 (gap identification)

---

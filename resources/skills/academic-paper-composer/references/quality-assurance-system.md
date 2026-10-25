# Quality Assurance System

Part of the academic-paper-composer skill. Load only this file for this topic.

### Quality Standards Reference

For detailed evaluation criteria, all standards are defined in:
```markdown
references/writing_standards.md
```

This document provides:
- Chapter-level quality standards (5 dimensions)
- Final quality standards (7 dimensions)
- Section-specific quality criteria
- Scoring rubrics
- Issue identification and fixes

### Section Writing Guides

For guidance on writing each section type:
```markdown
references/section_guides.md
```

This provides:
- Abstract writing template and checklist
- Introduction structure (6 subsections)
- Main body chapter templates (4 types)
- Conclusion structure
- Transition strategies
- Platform-specific style guidance
- Common mistakes and fixes

### Evaluation Scripts

Two Python scripts support quality validation:

#### 1. Chapter Quality Check
```bash
python scripts/chapter_quality_check.py
```

**Function**: Evaluates individual chapters against 5-dimension standards
- Creates evaluation templates
- Calculates scores and pass/fail
- Identifies weak dimensions
- Generates revision recommendations
- Supports multi-chapter comparison

**When to Use**: After writing each chapter (Step 4.2.C)

#### 2. Final Paper Evaluation
```bash
python scripts/final_evaluation.py
```

**Function**: Evaluates complete paper against 7-dimension standards
- Comprehensive quality assessment
- Completeness checklist validation
- Submission readiness determination
- Platform-specific preparation
- Generates final report with recommendations

**When to Use**: After all chapters complete (Step 5.2)

---

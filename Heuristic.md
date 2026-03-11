Heuristic Hash Engine — this is where your reconciliation system becomes intelligent and fintech-grade.

This engine will:

✅ Match even if date differs
✅ Match even if reference missing
✅ Match even if description different
✅ Match even if amount slightly different
✅ Generate confidence score
✅ Prepare data for AI RAG explanation layer
✅ Keep logging + failure safety


Instead of strict key:

(amount, date, reference)

We use candidate bucket search:

Step 1

Group Yardi transactions by rounded amount

Step 2

For each bank transaction:

Search candidate transactions where:

amount difference <= tolerance
date difference <= tolerance
description similarity >= threshold
Step 3

Compute:

confidence_score = weighted_score
Step 4

Choose best candidate
Remove from pool → prevents duplicate reuse
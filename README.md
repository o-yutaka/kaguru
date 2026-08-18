# Kaggriculture Official Competition

Dedicated repository for the Kaggle `kaggriculture` competition.

## Scope
- Submission code
- Replay analysis
- Evaluation / regression harness
- Kaggle submission workflows
- Competition-specific research artifacts

## Separation
This repository is independent of BLACK and HROS-dev production code.

## Authentication
Kaggle credentials are never committed. GitHub Actions may use the optional repository secret `KAGGRICULTURE_KAGGLE_API_TOKEN` first, with existing Kaggle secret aliases as fallback.

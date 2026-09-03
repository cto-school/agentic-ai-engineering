# Shared Course Components

This directory is intentionally small. Each day currently keeps its reference code
near its notebooks so beginners can see the mechanism being taught before meeting a
shared abstraction. Day 5 then performs the explicit consolidation into a harness.

Potential future components, only if repeated maintenance justifies extraction:

```text
shared/
├── model_clients/       # local, hosted, and mock model routes
├── notebook_helpers/    # environment and display helpers
├── mock_models/         # deterministic teaching/test responses
├── mock_tools/          # simulated search, calendar, email, and tasks
├── evaluation/          # small reusable checks
└── sample_data/         # compact, redistribution-safe datasets
```

## Rule for shared abstractions

Do not move a mechanism into shared code before students have seen or implemented its essential behavior. For example, Day 1 should show the tool loop before later projects import a reusable runtime.

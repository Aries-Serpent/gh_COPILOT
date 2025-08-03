# Success Criteria

## Quantitative Goals
- Code coverage must remain above **95%**.
- Compliance score should be **0.9** or higher.

## Stakeholder Sign-off Workflow
Stakeholders sign off only after validation steps in [`validation/protocols`](../validation/protocols)
confirm regulatory and process compliance.

## Latency and Failure Handling
- Latency checks ensure each validation completes in under one minute.
- Any run exceeding the threshold triggers a retry and logs the failure for review.
- Persistent failures escalate to the compliance team for resolution.

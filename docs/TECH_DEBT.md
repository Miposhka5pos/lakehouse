# Technical Debt

This page tracks deferred engineering work that is intentionally out of scope for the current MVP.

## Spark Runner

- [ ] **Recover job state after Runner restart.** Reconcile persisted Runner jobs with Spark Standalone applications after the Runner container restarts; distinguish a lost local `spark-submit` process from a Spark application that is still running.
- [ ] **Support parallel Spark jobs.** Replace the MVP single-job execution constraint with configurable concurrency and define scheduling/queue behavior.
- [ ] **Support job cancellation.** Add an API operation to cancel a submitted or running job and propagate cancellation to the Spark application.
- [ ] **Add job execution timeouts.** Allow a configurable maximum runtime and define timeout handling, process termination, and final job status.

## MVP constraints

Until the items above are implemented:

- Runner executes at most one Spark job at a time.
- No job cancellation endpoint is provided.
- Jobs have no automatic execution timeout.
- After an unexpected Runner restart, the state of an in-flight job may require manual investigation.

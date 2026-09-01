# Final package validation

## Static validation performed before handover

The final-review package was checked outside the TRE using only code/configuration and toy in-memory data:

```bash
python -m compileall -q src scripts tests
PYTHONPATH=src pytest -q
```

Result at handover:

```text
5 passed
```

The tests cover:

- propensity-score design smoke execution on generated toy data;
- candidate-K selection logic;
- real-TRE patient/event identifier resolution using cross-source overlap rather than hash-name intuition;
- Stage 02 missingness classification and Sports-vs-Wider difference flagging;
- aggregate stage-summary audit output and next-step command behaviour.

A separate six-source toy cleaning smoke test was also run to confirm that Stage 02:

- resolves patient/event identifier roles;
- cleans all six canonical source families;
- writes column-level missingness outputs;
- prints integrity/missingness key findings;
- writes aggregate stage audit files; and
- points to Stage 03 as the next command.

## What these tests do not prove

They do not validate the contents of the real BTH extracts. Real-data source semantics, extract coverage, missingness, linkage, positivity, balance, event coding and model adequacy must still be established by the TRE run.

## Required repeat after TRE ingress

From the ingressed project root:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
python -m compileall -q src scripts tests
python -m pytest -q
```

Record the resulting package/dependency versions in the run manifest created by the orchestrated workflow.

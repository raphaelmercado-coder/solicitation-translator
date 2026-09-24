# Solicitation Translator: repo map for agents

People start at `README.md`. This file is for an agent working in the repo.

| If the job is... | Go to | Read first |
|---|---|---|
| Translating a notice | `translator/` | `translator/identity.md` |
| Checking an output | `tests/` | the docstring at the top of `tests/verify.py` |
| Seeing what happened in past runs | `runs/` | `runs/RUN-LOG.md` |

## Rules

- **When translating, load `translator/` and the notice files only.** Do
  not open `tests/`, `runs/` or `inputs/` for help. They hold the checker,
  past outputs and the test notices. Reading them while translating is
  reading the answer key.
- `translator/` is the product. Change it only with the owner's approval.
  After any change, rerun `python3 tests/selftest.py` and every
  `runs/*/run4-output.md` through `tests/verify.py`.
- Never edit a past run's output or verify result. Add a new run and log it
  in `runs/RUN-LOG.md`.

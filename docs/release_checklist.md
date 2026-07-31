# Release checklist

## Before the first public push

- [x] Confirm the repository name and package URLs in `pyproject.toml`.
- [x] Replace “SPRUCE contributors” with the preferred copyright attribution
      (`LICENSE`, `NOTICE`: Myles McDaniel).
- [x] Review Apache-2.0 with the project owner. Declared as a PEP 639 SPDX
      expression with `LICENSE` and `NOTICE` shipped as license files.
- [x] Confirm no `.env`, tokens, private prompts, model weights, or
      checkpoints are tracked. `.gitignore` covers `.env`, `*.pt`,
      `*.safetensors`, `dist/`, `.venv/`, and editor/agent state.
- [ ] Run `python -m pytest -q`.
- [ ] Run `python -m build`.
- [ ] Run `python -m twine check dist/*`.
- [ ] Install the wheel in a clean environment.
- [ ] Run `sprucekit info`.
- [ ] Run the Colab quickstart on a fresh GPU runtime.

`pytest`, `build`, and `twine check` also run in CI on Python 3.10, 3.11, and
3.12 (`.github/workflows/ci.yml`), so the first push exercises them. Run them
locally first anyway — a red first commit is a bad first impression.

## Before PyPI

- [ ] Create the `sprucekit` project or a pending trusted publisher on
      PyPI.
- [ ] Configure the GitHub `pypi` environment used by
      `.github/workflows/publish.yml`.
- [ ] Publish `0.1.0rc1` to TestPyPI.
- [ ] Install and smoke-test the TestPyPI wheel.
- [ ] Tag the final release `v0.1.0`. The publish workflow triggers on `v*`
      tags and uses trusted publishing, so no API token is stored in the repo.

## Claim review

- Keep Qwen2.5-Coder-1.5B as the only verified reader.
- Label other Qwen sizes experimental until frozen cross-size validation.
- Quote hardware and timing boundaries with every latency number.
- Do not treat the 288 rows as 288 independent semantic tasks.
- Do not use reserved-memory results as compiler-only memory.
- Do not present asymptotic complexity as a wall-clock comparison.

## Provenance

`RELEASE_MANIFEST.md` records what ships, what is deliberately excluded, and
the SHA-256 of the sealed paper report. Recompute that hash before quoting a
number from the report:

```bash
python -c "import hashlib; print(hashlib.sha256(open('benchmarks/paper_results/natural_yarn_beam16/combined_report.json','rb').read()).hexdigest().upper())"
```

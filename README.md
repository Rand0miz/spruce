# SPRUCE

**Sparse, Preserving, Recursive, Unified Context Extension**

SPRUCE is a training-free hierarchical evidence compiler for long documents.
It locates query-relevant source regions before running the language model,
expands them to coherent paragraph boundaries, restores their exact original
text in source order, and asks an ordinary frozen model to read the resulting
compact packet.

The default runtime does not use model hidden states, attention matrices,
Q/K features, a trained selector, or a sparse-attention kernel.

## Install

Until the first PyPI release, install directly from GitHub:

```bash
pip install git+https://github.com/Rand0miz/spruce.git
```

After the PyPI release:

```bash
pip install sprucekit
```

A source checkout can also be installed in editable mode:

```bash
pip install -e .
```

SPRUCE does not bundle model weights. Models are downloaded separately under
their own licenses.

## Command line

Compile a document into an exact-text evidence packet:

```bash
sprucekit compile \
  --model Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --document book.txt \
  --question "Which alloy was required for the replacement collar?" \
  --output evidence.txt \
  --metadata evidence.json
```

Compile and run the model:

```bash
sprucekit answer \
  --model Qwen/Qwen2.5-Coder-1.5B-Instruct \
  --document book.txt \
  --question "Which alloy was required for the replacement collar?"
```

## Python API

```python
from transformers import AutoModelForCausalLM
from sprucekit import SpruceCompiler

model_name = "Qwen/Qwen2.5-Coder-1.5B-Instruct"
compiler = SpruceCompiler.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    attn_implementation="sdpa",
).to("cuda")

document = open("book.txt", encoding="utf-8").read()
answer, result = compiler.answer(
    model,
    document,
    "Which alloy was required for the replacement collar?",
)

print(answer)
print(result.packet.selected_blocks)
print(result.packet.compression_fraction)
```

The example above uses the frozen defaults, including `feature_dim=512`. On
documents beyond roughly 32K tokens, pass a wider sketch or retrieval will fail
silently — see [the `feature_dim` note](#how-it-works):

```python
from sprucekit import CompilerConfig, SpruceCompiler

compiler = SpruceCompiler.from_pretrained(
    model_name, config=CompilerConfig(feature_dim=4096))
```

Compilation can be used independently of model inference:

```python
result = compiler.compile(document, question)

print(result.content)     # human-readable evidence packet
print(result.prompt)      # model-ready chat prompt
print(result.metadata())  # source spans and selector accounting
```

## How it works

1. Tokenize the source prompt with character offsets.
2. Hash each 64-token block into a fixed-width lexical sketch.
3. Construct a deterministic radix-2 union tree.
4. Traverse top-down with a query-aware beam.
5. Keep the best four source blocks.
6. Expand by one neighboring block and paragraph boundaries.
7. Stitch exact source text in original order.
8. Run ordinary dense attention over the compact packet.

The frozen defaults are:

```text
block size       64
feature width    512
beam             16
selected blocks  4
block radius     1
boundary         paragraph
radix            2
IDF power        2.0
```

> [!IMPORTANT]
> **`feature width 512` is a paper-frozen value, not a good default for long
> documents.** Raise it before running the defaults above on anything past
> roughly 32K tokens. The selector's own internal default is 4096.
>
> Every token hashes into one of `feature_dim` slots, and each internal tree
> node holds the union of its children's sketches. Long or repetitive sources
> saturate the upper levels, leaving the beam nothing to discriminate on near
> the root, so it commits to the wrong subtree — **silently**. The compiler
> still returns a confident, well-formed packet containing none of the
> evidence, and the reader model will answer from whatever it was handed.
>
> **Rule of thumb: `feature_dim` ≳ document tokens ÷ `block_size`, rounded up
> to a power of two.**
>
> Measured on one 80K-token, highly repetitive document (~1,250 blocks):
>
> | `feature_dim` | Outcome |
> |---|---|
> | 512 (paper default) | evidence missed |
> | 1024 | evidence recovered |
> | 4096 (selector default) | evidence recovered |
>
> Symptom to watch for: `result.packet.selected_blocks` clustering in one
> region of the document instead of spanning it. That is the visible sign the
> traversal went wrong near the root.
>
> Raising `feature_dim` costs a few MB of CPU RAM and linear index time. It
> does **not** change packet size, GPU memory, latency, or compression — those
> are governed by `candidate_blocks` and `block_size`.

Index construction processes the complete source on CPU. The final model sees
only the compact packet, so context-dependent GPU allocation stays nearly
constant in the validated configuration. CPU tokenization and index memory
still grow with source length.

## Measured result

The first sealed, unscreened natural retrieval suite used one
Qwen2.5-Coder-1.5B-Instruct model on one NVIDIA A100-SXM4-40GB. It compared
full dense YaRN reading against the fully charged live compiler on 288 paired
prompts from 16K through 128K.

| Metric | Dense YaRN | SPRUCE compiler |
|---|---:|---:|
| Exact answers | 192/288 (66.7%) | 237/288 (82.3%) |
| Summed request time | 1,368.5 s | 142.8 s |
| Overall speedup | — | 9.58x |
| 128K median request | 10.709 s | 0.767 s |
| 128K allocated GPU memory | 15.58 GB | 3.27 GB |
| Median model input | 73,690 tokens | 1,849.5 tokens |

The compiler raw rate exceeded dense at every measured length. Fully charged
speedup increased from 2.49x at 16K to 14.08x at 128K.

These 288 rows come from 12 independent semantic cases repeated across lengths
and evidence depths. Row-level paired McNemar was significant, but the
predeclared semantic-case bootstrap interval crossed zero
([-5.56, +34.72] percentage points). This is a strong controlled-distribution
result, not a claim that SPRUCE generally improves every model or task.

Reproducibility tables, figures, configuration, and the complete paired report
are in
[`benchmarks/paper_results/natural_yarn_beam16`](benchmarks/paper_results/natural_yarn_beam16).

## Model compatibility

The selector is tokenizer-level and training-free; it was not trained on the
1.5B model. Qwen2.5-Coder-1.5B-Instruct is the currently verified reader.

| Reader | Status |
|---|---|
| Qwen2.5-Coder-0.5B-Instruct | Experimental; validation pending |
| Qwen2.5-Coder-1.5B-Instruct | Verified |
| Qwen2.5-Coder-3B-Instruct | Experimental; validation and model-license review pending |
| Qwen2.5-Coder-7B-Instruct | Experimental; validation pending |

Do not interpret “experimental” as a new selector-training requirement. The
first cross-size step is frozen evaluation of evidence recall, answer accuracy,
latency, and memory.

## Scope

The supported product path is exact-text evidence compilation followed by
ordinary dense generation over the compiled packet.

The research archive also contains learned sparse-attention conversion,
PyTorch/Triton kernels, residual-summary experiments, and failed ablations.
Those are not part of the default `sprucekit` runtime and should not be
confused with the compiler result above.

## Roadmap

SPRUCE is a complete, self-contained result: training-free hierarchical
evidence compilation, measured and reported above. It requires no trained
retriever, no selector checkpoint, and no custom attention kernel, and it is
usable today by anything that needs a long document read under a fixed context
budget.

One direction that capability opens is an agentic coding harness working across
large codebases within a bounded context. That work is not part of this
release, ships nothing today, and makes no claim on the results above. Roadmap
items describe direction, not commitments, and carry no timeline.

## Reproducibility and claims

- The backbone and selector settings were frozen for the sealed paper run.
- Prompts were not screened against dense correctness.
- Model loading, prompt synthesis, and one warm-up were excluded symmetrically.
- All live request costs after in-memory prompt arrival were charged.
- The exact source archive and prompt-bank hashes are recorded with the result.

Please cite measured numbers with their hardware, model, length, and timing
boundary. Do not present asymptotic complexity as a wall-clock comparison.

## Contributing

Issues and pull requests are welcome. See [CONTRIBUTING](CONTRIBUTING.md) for
the workflow, [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) for expected conduct, and
[SECURITY](SECURITY.md) for private vulnerability reporting. Changes to the
frozen beam-16 defaults must be evaluated on new development data, not the
opened paper-result bank.

## Citing

Citation metadata is in [CITATION.cff](CITATION.cff). Quote measured numbers
with the model, hardware, length, precision, prompt distribution, and timing
boundary they were produced under.

## License

SPRUCE source code is provided under the Apache License 2.0. Model weights,
tokenizers, and datasets are separate works governed by their respective
licenses. See [NOTICE](NOTICE).

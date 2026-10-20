"""Print the parameter registry as a Markdown table (docs tables are generated from it).

  python scripts/registry_table.py > docs/generated-parameters.md
"""
from repeat_neraca.params import Registry


def main() -> None:
    reg = Registry.load()
    print("| Parameter | Default | Range | Unit | Scope | Sampling | Confidence | Source |")
    print("|---|---|---|---|---|---|---|---|")
    for name, p in reg.params.items():
        rng = f"{p.range[0]:g} to {p.range[1]:g}"
        if p.outer_range:
            rng += f" (outer {p.outer_range[0]:g} to {p.outer_range[1]:g})"
        note = f" ({p.note})" if p.note else ""
        print(f"| `{name}` | {p.default:g} | {rng} | {p.unit} | {p.scope} | {p.sampling} | "
              f"{p.confidence} | {p.source}{note} |")


if __name__ == "__main__":
    main()

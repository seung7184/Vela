# Review Checklist

Use this checklist before merging any Vela PR.

## Safety

- [ ] No live trading code was added.
- [ ] No broker execution code was added.
- [ ] No secrets were committed.
- [ ] Reports include the education-only disclaimer.

## Quality

- [ ] Tests pass.
- [ ] New behavior has tests.
- [ ] Functions are small and readable.
- [ ] Network calls are injectable or mockable.

## Investment discipline

- [ ] Every ticker report includes the VWCE alternative test.
- [ ] Every ticker report includes bull and bear cases.
- [ ] Every ticker report defines what would change the thesis.

# Fix: sed -i macOS vs Linux syntax

## Problem
`sed -i ""` is macOS syntax. On the Ubuntu CI runner, `""` is interpreted as a filename, not as the backup suffix flag.

## Fix
In `release.config.js`, change:

```js
// Before (macOS syntax):
'sed -i "" "s/^version = .*/version = \\"${nextRelease.version}\\"/" pyproject.toml && uv lock'

// After (Linux syntax):
'sed -i "s/^version = .*/version = \\"${nextRelease.version}\\"/" pyproject.toml && uv lock'
```

Just remove the `""` after `-i`.

## Commit
```
fix(ci): use Linux sed syntax in release.config.js
```

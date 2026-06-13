# Releasing

This document describes the one-time setup and the per-release steps needed to
publish a new version of `tju` to PyPI and GitHub.

## One-time setup (first release only)

### 1. Enable GitHub Pages

1. Go to **Settings → Pages** in the GitHub repository.
2. Under **Build and deployment → Source**, select **GitHub Actions**.
3. Save.  The docs workflow will deploy automatically on the next push to `main`.

### 2. Configure PyPI trusted publishing (OIDC — no token needed)

1. Go to <https://pypi.org/manage/account/publishing/> (log in to PyPI first).
2. Under **Add a new pending publisher**, fill in:
   - **PyPI project name:** `tju`
   - **Owner:** `tjuse`
   - **Repository name:** `tju-python`
   - **Workflow filename:** `publish.yml`
   - **Environment name:** `pypi`
3. Click **Add**.  No API token is needed — PyPI will accept the GitHub OIDC identity.

### 3. Create the `pypi` GitHub Actions environment

1. Go to **Settings → Environments → New environment**.
2. Name it `pypi`.
3. (Optional) Add a protection rule requiring a reviewer before deployment.

---

## Per-release checklist

```sh
# 1. Make sure all changes are committed and pushed to main
git status

# 2. Update the version in pyproject.toml
#    e.g. change  version = "0.1.0"  →  version = "0.2.0"
$EDITOR pyproject.toml

# 3. Update CHANGELOG.md
#    - Move items from [Unreleased] into a new ## [0.2.0] - YYYY-MM-DD section
#    - Add a new empty ## [Unreleased] at the top
#    - Update the compare links at the bottom
$EDITOR CHANGELOG.md

# 4. Commit the release
git add pyproject.toml CHANGELOG.md
git commit -m "chore: release v0.2.0"
git push

# 5. Tag and push — this triggers the publish workflow
git tag v0.2.0
git push --tags
```

GitHub Actions will then:
- ✅ Build sdist + wheel (`uv build`)
- ✅ Check the distribution (`uvx twine check dist/*`)
- ✅ Publish to PyPI via OIDC trusted publishing
- ✅ Create a GitHub Release with the changelog section as release notes
- ✅ Deploy the updated docs to GitHub Pages

## Verifying the release

```sh
pip install tju==0.2.0
python -c "import tju; print(tju.__doc__)"
```

Check:
- <https://pypi.org/project/tju/> — new version appears
- <https://python.tjuse.com/> — docs updated
- <https://github.com/tjuse/tju-python/releases> — GitHub Release created

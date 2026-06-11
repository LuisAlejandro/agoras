================
Maintainer Guide
================

If you are reading this, you probably forgot how to release a new version. Keep
reading.

Making a new release
--------------------

1. Start your project with a cookiecutter template.

2. Start your git flow workflow.
::

    git flow init

3. Create a new milestone in GitHub. Plan the features of your new release. Assign
existing bugs to your new milestone.

4. Start a new feature.
::

    git flow feature start <feature name>

5. Code, code and code. More coding. Mess it up several times. Push to feature
branch. Watch Travis go red. Write unit tests. Watch Travis go red again. Don't
leave uncommitted changes.

6. Finish your feature.
::

    git flow feature finish <feature name>

7. Repeat 4-6 for every other feature you have planned for this release.

8. When you're done with the features and ready to publish, use one of the
automated release commands. This will handle version bumping, changelog updates,
git flow operations, and GitHub release creation automatically.
::

    make release-patch    # For patch releases (bug fixes)
    make release-minor    # For minor releases (new features)
    make release-major    # For major releases (breaking changes)

The release script will:
- Start a git flow release
- Bump the version automatically
- Update the changelog (HISTORY.rst)
- Commit the changes
- Finish the git flow release
- Create a GitHub release (if GitHub CLI is configured)

9. The GitHub Actions workflow will automatically publish the packages to PyPI
when the GitHub release is created. No manual action is required.

10. Close the milestone in GitHub.

11. Write about your new version in your blog. Tweet it, post it on facebook.

Making a new hotfix
-------------------

1. Create a new milestone in GitHub. Assign existing bugs to your new milestone.

2. Code your hotfix.

3. When ready to publish, use the automated hotfix command. This will handle
version bumping (patch increment), changelog updates, git flow operations, and
GitHub release creation automatically.
::

    make hotfix

The hotfix script will:
- Start a git flow hotfix
- Bump the version automatically (patch increment)
- Update the changelog (HISTORY.rst)
- Commit the changes
- Finish the git flow hotfix
- Create a GitHub release (if GitHub CLI is configured)

4. The GitHub Actions workflow will automatically publish the packages to PyPI
when the GitHub release is created. No manual action is required.

5. Close the milestone in GitHub.

6. Write about your new version in your blog. Tweet it, post it on facebook.

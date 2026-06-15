#!/usr/bin/env bash
set -euo pipefail

APP_NAME=${1:-Hotfix}
NON_INTERACTIVE=${NON_INTERACTIVE:-false}

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() { echo -e "${GREEN}[HOTFIX]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if ! git rev-parse --git-dir >/dev/null 2>&1; then
    print_error "Not in a git repository"
    exit 1
fi

if ! git config --get gitflow.branch.master >/dev/null 2>&1; then
    print_warning "Git flow not initialized. Initializing with default settings..."
    git flow init -d
fi

CURRENT_VERSION=$(grep '^current_version = ' .bumpversion.cfg | awk '{print $3}')
if ! echo "$CURRENT_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    print_error "Current version is not a valid version"
    exit 1
fi
print_step "Current version: $CURRENT_VERSION"

NEW_VERSION=$(bumpversion --dry-run --list patch 2>/dev/null | grep '^new_version=' | cut -d'=' -f2-)
print_step "New hotfix version will be: $NEW_VERSION"

if [[ "$NON_INTERACTIVE" != "true" ]]; then
    read -p "Proceed with hotfix $NEW_VERSION? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Hotfix cancelled"
        exit 1
    fi
fi

print_step "Starting git flow hotfix: $NEW_VERSION"
git flow hotfix start "$NEW_VERSION"

print_step "Bumping version to $NEW_VERSION"
bumpversion --no-commit --new-version "$NEW_VERSION" patch



print_step "Updating changelog"
if command -v gitchangelog >/dev/null 2>&1; then
    gitchangelog >HISTORY.rst
else
    print_warning "gitchangelog not found, skipping changelog update"
fi

print_step "Committing version bump and changelog"
git add .
git commit -S -m "Updating Changelog and version to $NEW_VERSION"

print_step "Removing temporary tag"
git tag -d "$NEW_VERSION" 2>/dev/null || true

print_step "Configuring git for non-interactive mode"
git config --local core.editor ":"
git config --local merge.ours.driver true
export GIT_MERGE_AUTOEDIT=no
export GPG_TTY=$(tty) 2>/dev/null || true

print_step "Publishing hotfix branch to origin"
git push -u origin "hotfix/$NEW_VERSION"

print_step "Finishing git flow hotfix"
git flow hotfix finish -s -p -m "Hotfix version $NEW_VERSION" "$NEW_VERSION"

print_step "Removing remote hotfix branch"
git push origin --delete "hotfix/$NEW_VERSION" 2>/dev/null || true

git config --local --unset core.editor 2>/dev/null || true
git config --local --unset merge.ours.driver 2>/dev/null || true

print_step "Pushing master, develop, and tags to origin"
git push origin master develop --tags

print_step "Verifying tag was pushed to remote"
MAX_RETRIES=5
RETRY_DELAY=3
TAG_EXISTS=false

for i in $(seq 1 "$MAX_RETRIES"); do
    if git ls-remote --tags origin | grep -q "refs/tags/$NEW_VERSION$"; then
        TAG_EXISTS=true
        print_step "Tag $NEW_VERSION found on remote"
        break
    fi
    if [ "$i" -lt "$MAX_RETRIES" ]; then
        print_warning "Tag not found on remote, retrying in ${RETRY_DELAY}s... (attempt $i/$MAX_RETRIES)"
        sleep "$RETRY_DELAY"
        git push origin master develop --tags
    fi
done

if [ "$TAG_EXISTS" = false ]; then
    print_error "Tag $NEW_VERSION was not found on remote after $MAX_RETRIES attempts"
    print_error "Please verify the push manually: git push origin --tags"
    exit 1
fi

print_step "Creating GitHub release"
if command -v gh >/dev/null 2>&1; then
    if gh auth status >/dev/null 2>&1; then
        RELEASE_NOTES=""
        DESCRIPTION_TEXT=""
        if [ -f "RELEASE_DESCRIPTION.rst" ]; then
            DESCRIPTION_TEXT=$(cat RELEASE_DESCRIPTION.rst)
        fi

        if [ -f "HISTORY.rst" ]; then
            RELEASE_CONTENT=$(awk "/^$NEW_VERSION \(/ { flag=1; next } flag && /^[0-9]+\.[0-9]+\.[0-9]+ \(/ { exit } flag" HISTORY.rst)
            RELEASE_NOTES="$DESCRIPTION_TEXT

## What's new in $NEW_VERSION
$RELEASE_CONTENT

Read [HISTORY](HISTORY.rst) for more info.

**Full Changelog**: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/compare/$CURRENT_VERSION...$NEW_VERSION"
        fi

        print_step "Creating GitHub release $NEW_VERSION"
        if gh release create "$NEW_VERSION" \
            --title "$APP_NAME $NEW_VERSION (Hotfix)" \
            --notes "$RELEASE_NOTES" \
            --latest; then
            print_step "GitHub release created successfully!"
        else
            print_warning "Failed to create GitHub release. You can create it manually later."
        fi
    else
        print_warning "GitHub CLI not authenticated. Please run 'gh auth login' first."
        print_warning "You can create the GitHub release manually later."
    fi
else
    print_warning "GitHub CLI not found, skipping GitHub release creation"
fi

print_step "Hotfix $NEW_VERSION completed successfully!"

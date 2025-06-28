# X Rebrand Plan: Transition from Twitter to X

## Executive Summary

This document outlines a comprehensive plan to rebrand all Twitter references to "X" across the Agoras application. This change reflects Twitter's official rebrand to X and ensures our application stays current with the platform's identity.

## Scope Analysis

Based on codebase analysis, the following areas require updates:

### 1. Core Code Files

- **Python modules**: `agoras/core/twitter.py`, `agoras/core/api/twitter.py`
- **Authentication modules**: `agoras/core/api/auth/twitter.py`
- **Client modules**: `agoras/core/api/clients/twitter.py`
- **CLI interface**: `agoras/cli.py`
- **Base classes**: References in `agoras/core/base.py`

### 2. Documentation Files

- **User guides**: `docs/twitter.rst`
- **Credential guides**: `docs/credentials/twitter.rst`
- **Usage documentation**: `docs/usage.rst`, `USAGE.rst`
- **README files**: `README.rst`, `README.short.rst`
- **API documentation**: Various RST files

### 3. Configuration and Scripts

- **Test scripts**: `test-*.sh` files
- **Setup configuration**: `setup.py`
- **CLI parameters**: All `--twitter-*` parameters
- **Environment variables**: `TWITTER_*` environment variables

### 4. Asset Files

- **Documentation images**: 11 Twitter-related screenshots in `docs/credentials/images/`
- **Branding assets**: Need to be updated to reflect X branding

### 5. External References

- **URLs**: Links to twitter.com
- **API endpoints**: Twitter API references
- **Third-party documentation**: Links to Twitter developer docs

## Rebranding Strategy

### Naming Conventions

| Current | New | Context |
|---------|-----|---------|
| `twitter` | `x` | File names, variable names, lowercase references |
| `Twitter` | `X` | Class names, proper nouns, user-facing text |
| `TWITTER` | `X` | Environment variables, constants |
| `tweet` | `post` | Generic post references |
| `Tweet` | `Post` | Class references to posts |
| `retweet` | `repost` | Share functionality |

### Backward Compatibility

To maintain backward compatibility during transition:

1. **Dual Parameter Support**: Support both old and new parameter names
2. **Deprecation Warnings**: Add warnings for old parameter usage
3. **Alias Mapping**: Map old names to new names internally
4. **Documentation**: Clearly indicate deprecated vs. new parameters

## Technical Implementation Details

### 1. File Renaming Strategy

```
agoras/core/twitter.py → agoras/core/x.py
agoras/core/api/twitter.py → agoras/core/api/x.py
agoras/core/api/auth/twitter.py → agoras/core/api/auth/x.py
agoras/core/api/clients/twitter.py → agoras/core/api/clients/x.py
docs/twitter.rst → docs/x.rst
docs/credentials/twitter.rst → docs/credentials/x.rst
docs/credentials/images/twitter-*.png → docs/credentials/images/x-*.png
```

### 2. Code Changes

#### Class Renaming

```python
# Before
class Twitter(SocialNetwork):
class TwitterAPI(BaseAPI):
class TwitterAuthManager(BaseAuthManager):

# After
class X(SocialNetwork):
class XAPI(BaseAPI):
class XAuthManager(BaseAuthManager):
```

#### Parameter Renaming

```python
# CLI Parameters (with backward compatibility)
--twitter-consumer-key → --x-consumer-key
--twitter-consumer-secret → --x-consumer-secret
--twitter-oauth-token → --x-oauth-token
--twitter-oauth-secret → --x-oauth-secret
--tweet-id → --x-post-id
--twitter-video-url → --x-video-url
--twitter-video-title → --x-video-title
```

#### Environment Variables

```bash
# Old (deprecated)
TWITTER_CONSUMER_KEY → X_CONSUMER_KEY
TWITTER_CONSUMER_SECRET → X_CONSUMER_SECRET
TWITTER_OAUTH_TOKEN → X_OAUTH_TOKEN
TWITTER_OAUTH_SECRET → X_OAUTH_SECRET
TWEET_ID → X_POST_ID
```

### 3. Import Updates

All imports referencing Twitter modules need updates:

```python
# Before
from agoras.core.twitter import Twitter
from agoras.core.api.twitter import TwitterAPI

# After
from agoras.core.x import X
from agoras.core.api.x import XAPI
```

### 4. Network Identifier

Update network selection parameter:

```python
# CLI choices update
choices=['twitter', 'facebook', ...] → choices=['x', 'facebook', ...]
```

### 5. Documentation Updates

#### Content Updates

- Replace "Twitter" with "X" in user-facing documentation
- Update "tweet" to "post" where appropriate
- Replace "retweet" with "repost"
- Update all screenshots to reflect X branding
- Update external links from twitter.com to x.com

#### API Documentation

- Update all docstrings and comments
- Update parameter descriptions
- Update example code snippets

## Risk Assessment

### High Risk

- **Breaking Changes**: Existing users' scripts may break
- **API Compatibility**: Third-party integrations may fail
- **Configuration Files**: Existing config files with old parameter names

### Medium Risk

- **Documentation Drift**: Temporary inconsistency during transition
- **Search/Discovery**: Users may search for "Twitter" instead of "X"
- **External Dependencies**: Third-party libraries may still use Twitter terminology

### Low Risk

- **Asset Updates**: Screenshot updates are cosmetic
- **Internal Refactoring**: Code improvements without external impact

## Migration Strategy

### Backward Compatibility Layer

```python
# Example implementation
def _get_config_value(self, new_key, old_key=None, env_new=None, env_old=None):
    """Get config value with backward compatibility."""
    # Try new key first
    value = super()._get_config_value(new_key, env_new)

    # Fall back to old key with deprecation warning
    if value is None and old_key:
        value = super()._get_config_value(old_key, env_old)
        if value is not None:
            warnings.warn(f"Parameter '{old_key}' is deprecated. Use '{new_key}' instead.",
                         DeprecationWarning, stacklevel=2)

    return value
```

### Configuration Migration

```python
# Auto-migrate old configuration
def migrate_config(config):
    """Migrate old Twitter config to X config."""
    migration_map = {
        'twitter_consumer_key': 'x_consumer_key',
        'twitter_consumer_secret': 'x_consumer_secret',
        'twitter_oauth_token': 'x_oauth_token',
        'twitter_oauth_secret': 'x_oauth_secret',
        'tweet_id': 'x_post_id',
    }

    for old_key, new_key in migration_map.items():
        if old_key in config and new_key not in config:
            config[new_key] = config[old_key]
            print(f"Migrated {old_key} to {new_key}")

    return config
```

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goals**: Establish infrastructure for rebrand and maintain backward compatibility

**Tasks**:

1. **Setup deprecation framework**
   - [ ] Create deprecation warning system
   - [ ] Implement backward compatibility utilities
   - [ ] Add configuration migration helpers

2. **Core API updates**
   - [ ] Rename `TwitterAPI` → `XAPI`
   - [ ] Rename `TwitterAuthManager` → `XAuthManager`
   - [ ] Update `agoras/core/api/twitter.py` → `agoras/core/api/x.py`
   - [ ] Maintain old imports with deprecation warnings

3. **Configuration parameter mapping**
   - [ ] Add new X-based parameters to CLI
   - [ ] Implement parameter aliasing system
   - [ ] Add deprecation warnings for old parameters

**Deliverables**:

- Backward compatibility layer functional
- New X-based API classes available
- CLI accepts both old and new parameters

### Phase 2: Core Implementation (Week 2)

**Goals**: Update main Twitter implementation and client modules

**Tasks**:

1. **Main Twitter class updates**
   - [ ] Rename `Twitter` → `X` class
   - [ ] Update `agoras/core/twitter.py` → `agoras/core/x.py`
   - [ ] Update all internal method references
   - [ ] Update error messages and logging

2. **Client and auth modules**
   - [ ] Update `agoras/core/api/clients/twitter.py` → `agoras/core/api/clients/x.py`
   - [ ] Update `agoras/core/api/auth/twitter.py` → `agoras/core/api/auth/x.py`
   - [ ] Update authentication workflows

3. **CLI integration**
   - [ ] Update network choice from 'twitter' to 'x'
   - [ ] Update help text and descriptions
   - [ ] Add backward compatibility for 'twitter' network selection

**Deliverables**:

- X class fully functional
- All core modules renamed and updated
- Network selection supports both 'twitter' and 'x'

### Phase 3: Documentation and Assets (Week 3)

**Goals**: Update all documentation and visual assets

**Tasks**:

1. **Documentation updates**
   - [ ] Update `docs/twitter.rst` → `docs/x.rst`
   - [ ] Update `docs/credentials/twitter.rst` → `docs/credentials/x.rst`
   - [ ] Update `README.rst` and `README.short.rst`
   - [ ] Update `USAGE.rst` and `docs/usage.rst`
   - [ ] Update API documentation

2. **Asset updates** *(User will handle screenshots)*
   - [ ] Update all 11 Twitter screenshots to reflect X branding *(User responsibility)*
   - [ ] Rename image files: `twitter-*.png` → `x-*.png` *(User responsibility)*
   - [ ] Update image references in documentation
   - [ ] Update any logo or branding assets *(User responsibility)*

3. **Content updates**
   - [ ] Replace "Twitter" with "X" in user-facing content
   - [ ] Update "tweet" to "post" where appropriate
   - [ ] Update "retweet" to "repost"
   - [ ] Update external links from twitter.com to x.com

**Deliverables**:

- All documentation reflects X branding
- Screenshots updated with current X interface
- External links updated

### Phase 4: Testing and Scripts (Week 4)

**Goals**: Update test scripts and ensure comprehensive testing

**Tasks**:

1. **Test script updates**
   - [ ] Update `test-post.sh` for X parameters
   - [ ] Update `test-schedule.sh` for X parameters
   - [ ] Update `test.sh` main script
   - [ ] Update `test-last-from-feed.sh` and `test-random-feed.sh`

2. **Comprehensive testing**
   - [ ] Test backward compatibility with old parameters
   - [ ] Test new X parameters functionality
   - [ ] Test deprecation warnings
   - [ ] Test configuration migration

3. **Integration testing**
   - [ ] Test CLI with both old and new parameters
   - [ ] Test API functionality with X branding
   - [ ] Test documentation examples
   - [ ] Test error handling and messaging

**Deliverables**:

- All test scripts updated and functional
- Comprehensive test coverage for both X and legacy Twitter parameters
- Verified backward compatibility

### Phase 5: Cleanup and Optimization (Week 5)

**Goals**: Final cleanup and optimization of the rebranding

**Tasks**:

1. **Code cleanup**
   - [ ] Remove unnecessary imports
   - [ ] Optimize backward compatibility code
   - [ ] Update internal comments and docstrings
   - [ ] Ensure consistent naming throughout

2. **Documentation polish**
   - [ ] Review all documentation for consistency
   - [ ] Ensure examples work with new parameters
   - [ ] Update any missed references
   - [ ] Validate external links

3. **Performance optimization**
   - [ ] Profile backward compatibility overhead
   - [ ] Optimize parameter resolution
   - [ ] Cache migration mappings
   - [ ] Optimize imports

**Deliverables**:

- Clean, optimized codebase
- Polished documentation
- Efficient backward compatibility

### Phase 6: Release Preparation (Week 6)

**Goals**: Prepare for production release and user communication

**Tasks**:

1. **Release preparation**
   - [ ] Update version numbers
   - [ ] Prepare changelog with migration notes
   - [ ] Create migration guide for users
   - [ ] Update setup.py keywords

2. **User communication**
   - [ ] Prepare announcement about Twitter → X rebrand
   - [ ] Create migration timeline for users
   - [ ] Document deprecation schedule
   - [ ] Prepare FAQ for common issues

3. **Final validation**
   - [ ] End-to-end testing
   - [ ] Documentation review
   - [ ] Backward compatibility verification
   - [ ] Performance benchmarking

**Deliverables**:

- Production-ready release
- User migration documentation
- Communication materials
- Comprehensive testing report

## Success Metrics

### Technical Metrics

- [ ] 100% backward compatibility maintained
- [ ] All tests pass with both old and new parameters
- [ ] Zero breaking changes for existing users
- [ ] Documentation accuracy: 100% of examples work

### User Experience Metrics

- [ ] Migration guide completion rate
- [ ] User adoption of new X parameters
- [ ] Reduction in support tickets related to Twitter/X confusion
- [ ] User satisfaction with rebrand transition

### Code Quality Metrics

- [ ] Code coverage maintained at current levels
- [ ] No performance regression
- [ ] Consistent naming conventions throughout
- [ ] Clean deprecation warning implementation

## Future Considerations

### Long-term Maintenance

- **Deprecation Timeline**: Plan to remove old Twitter parameters after 6 months (confirmed)
- **API Evolution**: Monitor X API changes and adapt accordingly
- **User Feedback**: Collect and incorporate user feedback on rebrand
- **User Communication**: Notify existing users about rebrand and migration timeline

### Potential Challenges

- **X API Changes**: X may introduce breaking changes to their API
- **Terminology Evolution**: "Post" vs "Tweet" usage may vary among users
- **Brand Recognition**: Users may still search for "Twitter" instead of "X"

## Conclusion

This comprehensive rebrand plan ensures a smooth transition from Twitter to X branding while maintaining backward compatibility and providing clear migration paths for users. The phased approach minimizes risk and allows for iterative feedback and improvement.

The implementation will be completed over 6 weeks, with each phase building upon the previous one to ensure stability and quality throughout the transition.

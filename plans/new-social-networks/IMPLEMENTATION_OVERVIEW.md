# Social Networks Implementation Overview

## Executive Summary

This document provides a comprehensive plan for adding four new social networks to agoras: Threads, Pinterest, Bluesky, and Mastodon. All implementations follow established OAuth 2.0 patterns and maintain full feature parity with existing platforms.

## Implementation Priority

### HIGH Priority (Implement First)

1. **Threads** - Meta's Twitter competitor with business account requirements
2. **Pinterest** - Visual content platform with pin-based system

### MEDIUM Priority (Implement After)

3. **Bluesky** - Decentralized social network using AT Protocol
4. **Mastodon** - Fediverse platform with multi-instance support

## Platform Comparison

| Platform | Authentication | Library | Key Features | Special Considerations |
|----------|---------------|---------|--------------|----------------------|
| **Threads** | OAuth 2.0 | threadspipepy | Posts, Reposts, Replies, Analytics | Business account required |
| **Pinterest** | OAuth 2.0 | pinterest-python-generated-api-client | Pins, Boards, Analytics | Creates separate pins for multiple images |
| **Bluesky** | OAuth 2.0 + Password | atproto | Posts, Replies, Quotes, Likes | AT Protocol, decentralized |
| **Mastodon** | OAuth 2.0 | Mastodon.py | Toots, Boosts, Favorites | Multi-instance, auto app registration |

## Dependencies to Add

```
# High Priority
threadspipepy>=0.4.5
pinterest-python-generated-api-client>=0.5.0

# Medium Priority
atproto>=0.0.46
Mastodon.py>=1.8.1
```

## Architecture Patterns

All platforms follow the established 4-layer architecture:

1. **Auth Layer** (`agoras/core/api/auth/{platform}.py`)
   - OAuth 2.0 authentication managers
   - Token caching and refresh logic
   - Platform-specific credential handling

2. **Client Layer** (`agoras/core/api/clients/{platform}.py`)
   - HTTP wrappers around platform libraries
   - Error handling and retry logic
   - Platform-specific API formatting

3. **API Layer** (`agoras/core/api/{platform}.py`)
   - Main integration classes
   - Async method wrappers
   - Authentication management

4. **Core Layer** (`agoras/core/{platform}.py`)
   - SocialNetwork interface implementation
   - Media system integration
   - Configuration management

## Feature Implementation Matrix

| Feature | Threads | Pinterest | Bluesky | Mastodon |
|---------|---------|-----------|---------|----------|
| **Text Posts** | ✅ | ✅ (as Pin descriptions) | ✅ | ✅ |
| **Images** | ✅ (up to 4) | ✅ (separate pins) | ✅ (up to 4) | ✅ (with alt text) |
| **Videos** | ✅ | ✅ | ✅ | ✅ |
| **Links** | ✅ | ✅ (destination URLs) | ✅ (embeds) | ✅ |
| **Like/Favorite** | ❌ (not supported) | ❌ (not supported) | ✅ | ✅ |
| **Share/Repost** | ✅ (Repost) | ❌ (not supported) | ✅ (Repost/Quote) | ✅ (Boost) |
| **Reply** | ✅ | ❌ (not applicable) | ✅ | ✅ |
| **Delete** | ❌ (not supported) | ✅ | ✅ | ✅ |
| **Analytics** | ✅ | ✅ | ❌ (limited) | ❌ (limited) |
| **RSS Feeds** | ✅ (inherited) | ✅ (inherited) | ✅ (inherited) | ✅ (inherited) |
| **Scheduling** | ✅ (inherited) | ✅ (inherited) | ✅ (inherited) | ✅ (inherited) |

## Configuration Requirements

### Required Variables by Platform

**Threads:**

- `THREADS_APP_ID` - Meta Developer App ID
- `THREADS_APP_SECRET` - Meta Developer App Secret
- `THREADS_REDIRECT_URI` - OAuth callback URL

**Pinterest:**

- `PINTEREST_APP_ID` - Pinterest Developer App ID
- `PINTEREST_APP_SECRET` - Pinterest Developer App Secret
- `PINTEREST_REDIRECT_URI` - OAuth callback URL

**Bluesky:**

- `BLUESKY_IDENTIFIER` - Username, email, or DID
- Either `BLUESKY_PASSWORD` OR (`BLUESKY_OAUTH_CLIENT_ID` + `BLUESKY_OAUTH_CLIENT_SECRET`)

**Mastodon:**

- `MASTODON_INSTANCE_URL` - Instance URL (e.g., <https://mastodon.social>)
- Optional: `MASTODON_CLIENT_ID`, `MASTODON_CLIENT_SECRET` (auto-generated if missing)

## Platform-Specific Features

### Threads

- **Unique Actions**: `reply` - Reply to posts
- **Reply Controls**: Configure who can reply to posts
- **Business Requirements**: Meta business account verification required

### Pinterest

- **Unique Actions**: `create-board`, `analytics`
- **Board Management**: Automatic board creation and selection
- **Pin Behavior**: Multiple images create separate pins (not carousel)

### Bluesky

- **Unique Actions**: `reply`, `quote`
- **Authentication Options**: Password OR OAuth 2.0
- **Decentralized**: Support for custom PDS servers
- **Character Limit**: 300 characters

### Mastodon

- **Unique Actions**: `reply`, `boost`
- **Multi-Instance**: Support any Mastodon instance
- **Auto Registration**: Automatic app registration per instance
- **Variable Limits**: Instance-specific character limits (500-5000+)
- **Accessibility**: Alt text support for images

## New CLI Actions

### Global New Actions

- `reply` - Reply to posts (Threads, Bluesky, Mastodon)

### Platform-Specific Actions

- **Pinterest**: `create-board`, `analytics`
- **Bluesky**: `quote`
- **Mastodon**: `boost` (alias for share)

## Files to Create (Total: 16 files)

### Core Files

```
agoras/core/threads.py
agoras/core/pinterest.py
agoras/core/bluesky.py
agoras/core/mastodon.py
```

### API Integration Files

```
agoras/core/api/threads.py
agoras/core/api/pinterest.py
agoras/core/api/bluesky.py
agoras/core/api/mastodon.py
```

### Authentication Files

```
agoras/core/api/auth/threads.py
agoras/core/api/auth/pinterest.py
agoras/core/api/auth/bluesky.py
agoras/core/api/auth/mastodon.py
```

### Client Files

```
agoras/core/api/clients/threads.py
agoras/core/api/clients/pinterest.py
agoras/core/api/clients/bluesky.py
agoras/core/api/clients/mastodon.py
```

## Files to Update

### Package Imports

```
agoras/core/__init__.py
agoras/core/api/__init__.py
agoras/core/api/auth/__init__.py
agoras/core/api/clients/__init__.py
```

### Dependencies

```
requirements.txt
```

## Documentation to Create

### Credential Setup Guides

```
docs/credentials/threads.rst
docs/credentials/pinterest.rst
docs/credentials/bluesky.rst
docs/credentials/mastodon.rst
```

### Usage Documentation

```
docs/threads.rst
docs/pinterest.rst
docs/bluesky.rst
docs/mastodon.rst
```

### API Documentation Updates

```
docs/api.rst (update to include new modules)
```

## Implementation Timeline

### Phase 1: High Priority Platforms (Weeks 1-4)

**Week 1-2: Threads Implementation**

- OAuth 2.0 authentication with threadspipepy
- Basic posting and media handling
- Reply and repost functionality
- Documentation and testing

**Week 3-4: Pinterest Implementation**

- OAuth 2.0 authentication with Pinterest API
- Pin creation and board management
- Multiple image handling (separate pins)
- Analytics integration

### Phase 2: Medium Priority Platforms (Weeks 5-8)

**Week 5-6: Bluesky Implementation**

- AT Protocol authentication (OAuth + password options)
- Post creation with blob handling
- Reply and quote functionality
- Custom server support

**Week 7-8: Mastodon Implementation**

- Multi-instance OAuth 2.0 authentication
- Status creation with instance-aware limits
- Reply, boost, and favorite functionality
- Auto app registration

## Quality Assurance

### Testing Strategy

1. **Unit Tests**: Individual component testing for each platform
2. **Integration Tests**: End-to-end OAuth flows and posting
3. **Media Tests**: Image/video upload and validation
4. **Error Tests**: Various failure scenarios and error handling
5. **Business Tests**: Platform-specific requirements validation

### Documentation Requirements

1. **Credential Setup**: Detailed guides with screenshots for each platform
2. **Usage Examples**: Comprehensive CLI usage examples
3. **Troubleshooting**: Common issues and solutions
4. **API Reference**: Complete API documentation updates

## Risk Assessment

### High Risk

- **Threads**: Meta business account verification requirements
- **Pinterest**: Rate limiting (200 requests/hour per user)

### Medium Risk

- **Bluesky**: AT Protocol still evolving, limited server adoption
- **Mastodon**: Instance availability and federation complexity

### Low Risk

- All platforms have mature, well-maintained Python libraries
- Established OAuth 2.0 patterns reduce authentication risk
- Existing agoras architecture provides solid foundation

## Success Metrics

### Technical Success Criteria

- [ ] All 4 platforms fully integrated with OAuth 2.0
- [ ] Full SocialNetwork interface compliance
- [ ] Media system integration working for all platforms
- [ ] RSS feed integration working for all platforms
- [ ] Google Sheets scheduling working for all platforms
- [ ] Comprehensive error handling implemented
- [ ] Complete test coverage achieved

### Documentation Success Criteria

- [ ] Credential setup guides completed with screenshots
- [ ] Usage documentation with comprehensive examples
- [ ] API documentation updated for all new modules
- [ ] Troubleshooting guides for common issues
- [ ] Business account requirement documentation

### Business Success Criteria

- [ ] Meta business account verification process documented
- [ ] Pinterest rate limiting properly handled
- [ ] Bluesky custom server support working
- [ ] Mastodon multi-instance support validated
- [ ] All platform-specific requirements met

## Maintenance Considerations

### Ongoing Requirements

1. **Library Updates**: Monitor and update platform libraries
2. **API Changes**: Track platform API changes and deprecations
3. **Business Requirements**: Monitor changes in business account requirements
4. **Rate Limiting**: Adjust rate limiting strategies as platforms evolve
5. **Security**: Keep OAuth implementations updated with security best practices

### Monitoring Points

1. **Authentication Success Rates**: Track OAuth flow success
2. **API Error Rates**: Monitor platform-specific error rates
3. **Media Upload Success**: Track media handling success rates
4. **Instance Health**: Monitor Mastodon instance availability
5. **Business Account Status**: Track Meta business verification status

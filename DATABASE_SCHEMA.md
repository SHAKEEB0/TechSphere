# TechSphere Database Schema

## Complete Database Design

### Users & Accounts

#### User Model
```
User (Custom User Model)
├── id: UUID (Primary Key)
├── username: CharField (unique, max 150)
├── email: EmailField (unique)
├── first_name: CharField
├── last_name: CharField
├── password_hash: CharField
├── is_active: Boolean (default: True)
├── is_staff: Boolean (default: False)
├── is_superuser: Boolean (default: False)
├── date_joined: DateTimeField (auto_now_add)
├── last_login: DateTimeField (nullable)
├── updated_at: DateTimeField (auto_now)
└── Indexes: email, username, date_joined
```

#### UserProfile Model
```
UserProfile
├── id: UUID (Primary Key)
├── user: ForeignKey(User, OneToOne)
├── avatar: ImageField (stored in R2)
├── bio: TextField (max 500 chars)
├── website: URLField (nullable)
├── location: CharField (max 100)
├── github_url: URLField (nullable)
├── twitter_handle: CharField (nullable)
├── linkedin_url: URLField (nullable)
├── verified: Boolean (default: False)
├── is_author: Boolean (default: False)
├── author_bio: TextField (for author profile)
├── social_accounts: JSONField (for OAuth connections)
├── preferences: JSONField (notification, theme, etc.)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: user, is_author, verified, created_at
```

#### Author Model
```
Author
├── id: UUID (Primary Key)
├── user: ForeignKey(User)
├── profile: ForeignKey(UserProfile)
├── slug: SlugField (unique)
├── about: TextField
├── featured_image: ImageField (R2)
├── total_posts: PositiveIntegerField (cached)
├── total_views: PositiveIntegerField (cached)
├── is_featured: Boolean (default: False)
├── is_approved: Boolean (default: False)
├── approved_at: DateTimeField (nullable)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: slug, is_featured, is_approved, created_at
    Foreign Keys: user, profile
    Unique Constraint: (user, slug)
```

### Blog Content

#### Category Model
```
Category
├── id: UUID (Primary Key)
├── name: CharField (max 100, unique)
├── slug: SlugField (unique)
├── description: TextField
├── featured_image: ImageField (R2, nullable)
├── parent: ForeignKey(Category, nullable, on_delete=CASCADE)
├── icon: CharField (FontAwesome icon, nullable)
├── color: CharField (hex color code)
├── order: PositiveIntegerField (for sorting)
├── seo_title: CharField (max 60)
├── seo_description: CharField (max 160)
├── meta_keywords: CharField
├── is_active: Boolean (default: True)
├── total_posts: PositiveIntegerField (cached)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: slug, parent, is_active, order, created_at
    Tree Structure: parent - child categories allowed
```

#### Tag Model
```
Tag
├── id: UUID (Primary Key)
├── name: CharField (max 50, unique)
├── slug: SlugField (unique)
├── description: CharField (max 200)
├── color: CharField (hex color code, nullable)
├── total_posts: PositiveIntegerField (cached)
├── is_active: Boolean (default: True)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: slug, is_active, created_at, name
```

#### Post Model
```
Post
├── id: UUID (Primary Key)
├── author: ForeignKey(Author)
├── title: CharField (max 200)
├── slug: SlugField (unique_for_date='published_at')
├── category: ForeignKey(Category)
├── tags: ManyToManyField(Tag)
├── content: TextField (HTML from CKEditor)
├── excerpt: CharField (max 300, for preview)
├── featured_image: ImageField (R2)
├── alt_text: CharField (for featured image)
├── status: CharField (draft, published, scheduled)
│   - Choices: DRAFT, PUBLISHED, SCHEDULED
├── published_at: DateTimeField (nullable)
├── scheduled_for: DateTimeField (nullable, for future posts)
├── updated_at: DateTimeField (auto_now)
├── view_count: PositiveIntegerField (default: 0, cached)
├── reading_time: PositiveIntegerField (in minutes, auto-calculated)
├── word_count: PositiveIntegerField (auto-calculated)
├── is_featured: Boolean (default: False)
├── is_pinned: Boolean (default: False)
├── enable_comments: Boolean (default: True)
├── enable_likes: Boolean (default: True)
├── enable_sharing: Boolean (default: True)
├── is_sponsored: Boolean (default: False)
├── sponsored_by: ForeignKey(Sponsorship, nullable)
├── seo_title: CharField (max 60)
├── seo_description: CharField (max 160)
├── seo_keywords: CharField (comma-separated)
├── canonical_url: URLField (nullable, for syndicated content)
├── og_image: URLField (auto-set from featured_image)
├── schema_type: CharField (Article, BlogPosting, NewsArticle)
├── created_at: DateTimeField (auto_now_add)
└── Indexes: slug, author, category, status, published_at
             is_featured, is_pinned, view_count, created_at
    Full-Text Search: title, excerpt, content
    Unique Constraint: (slug, published_at.year, published_at.month)
```

#### PostView Model
```
PostView (Analytics Tracking)
├── id: UUID (Primary Key)
├── post: ForeignKey(Post)
├── user: ForeignKey(User, nullable - for anonymous)
├── session_id: CharField (for anonymous tracking)
├── ip_address: GenericIPAddressField
├── user_agent: CharField (max 300)
├── referrer: URLField (nullable)
├── viewed_at: DateTimeField (auto_now_add)
├── time_spent: PositiveIntegerField (seconds)
└── Indexes: post, user, session_id, viewed_at
    Retention: 90 days (old records archived or deleted)
```

#### PostLike Model
```
PostLike
├── id: UUID (Primary Key)
├── post: ForeignKey(Post)
├── user: ForeignKey(User)
├── created_at: DateTimeField (auto_now_add)
└── Unique Constraint: (post, user)
    Indexes: post, user, created_at
```

#### PostBookmark Model
```
PostBookmark
├── id: UUID (Primary Key)
├── post: ForeignKey(Post)
├── user: ForeignKey(User)
├── collection: CharField (default: "default", for organizing bookmarks)
├── created_at: DateTimeField (auto_now_add)
└── Unique Constraint: (post, user)
    Indexes: post, user, created_at
```

#### ReadingHistory Model
```
ReadingHistory
├── id: UUID (Primary Key)
├── user: ForeignKey(User)
├── post: ForeignKey(Post)
├── is_completed: Boolean (default: False)
├── progress: PositiveIntegerField (0-100, scroll percentage)
├── first_read: DateTimeField (auto_now_add)
├── last_read: DateTimeField (auto_now)
├── read_count: PositiveIntegerField (default: 1)
└── Indexes: user, post, last_read
    Unique Constraint: (user, post)
```

### Comments System

#### Comment Model
```
Comment
├── id: UUID (Primary Key)
├── post: ForeignKey(Post)
├── author: ForeignKey(User)
├── parent: ForeignKey(Comment, nullable - for nested comments)
├── content: TextField (markdown or plain text)
├── is_approved: Boolean (default: False - pending moderation)
├── is_pinned: Boolean (default: False)
├── is_author_reply: Boolean (default: False)
├── likes_count: PositiveIntegerField (cached)
├── edit_count: PositiveIntegerField (default: 0)
├── last_edited_at: DateTimeField (nullable)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: post, author, parent, is_approved
             created_at, likes_count, is_pinned
    Unique Constraint: None (allow duplicate content)
    Tree Structure: Nested replies via parent field
```

#### CommentLike Model
```
CommentLike
├── id: UUID (Primary Key)
├── comment: ForeignKey(Comment)
├── user: ForeignKey(User)
├── created_at: DateTimeField (auto_now_add)
└── Unique Constraint: (comment, user)
    Indexes: comment, user, created_at
```

#### CommentFlag Model
```
CommentFlag
├── id: UUID (Primary Key)
├── comment: ForeignKey(Comment)
├── user: ForeignKey(User)
├── reason: CharField (spam, offensive, off-topic, etc.)
├── description: TextField
├── is_resolved: Boolean (default: False)
├── resolved_by: ForeignKey(User, nullable - admin)
├── resolution: CharField (deleted, approved, warning)
├── created_at: DateTimeField (auto_now_add)
└── Indexes: comment, user, is_resolved, created_at
    Unique Constraint: (comment, user)
```

### Newsletters

#### Newsletter Model
```
Newsletter
├── id: UUID (Primary Key)
├── name: CharField (max 100)
├── description: TextField
├── from_email: EmailField
├── from_name: CharField
├── reply_to_email: EmailField
├── frequency: CharField (daily, weekly, monthly)
├── day_of_week: IntegerField (for weekly, 0=Monday)
├── time_of_day: TimeField
├── template: TextField (HTML template)
├── is_active: Boolean (default: True)
├── subscriber_count: PositiveIntegerField (cached)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: is_active, frequency, created_at
```

#### NewsletterSubscriber Model
```
NewsletterSubscriber
├── id: UUID (Primary Key)
├── email: EmailField
├── newsletter: ForeignKey(Newsletter)
├── user: ForeignKey(User, nullable - for logged in users)
├── token: CharField (for unsubscribe link)
├── is_subscribed: Boolean (default: True)
├── is_verified: Boolean (default: False)
├── verification_token: CharField (for double opt-in)
├── subscribed_at: DateTimeField (auto_now_add)
├── unsubscribed_at: DateTimeField (nullable)
├── last_sent_at: DateTimeField (nullable)
├── bounce_count: PositiveIntegerField (default: 0)
├── is_bounced: Boolean (default: False)
├── metadata: JSONField (source, utm_params, etc.)
└── Indexes: email, is_subscribed, is_verified, created_at
    Unique Constraint: (email, newsletter)
    Soft Delete: is_subscribed flag
```

#### NewsletterIssue Model
```
NewsletterIssue
├── id: UUID (Primary Key)
├── newsletter: ForeignKey(Newsletter)
├── subject: CharField (max 100)
├── content: TextField (HTML)
├── status: CharField (draft, scheduled, sent, failed)
├── scheduled_at: DateTimeField (nullable)
├── sent_at: DateTimeField (nullable)
├── total_sent: PositiveIntegerField (default: 0)
├── total_opened: PositiveIntegerField (default: 0, cached)
├── total_clicked: PositiveIntegerField (default: 0, cached)
├── open_rate: DecimalField (calculated)
├── click_rate: DecimalField (calculated)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: newsletter, status, scheduled_at, sent_at, created_at
```

#### NewsletterClick Model
```
NewsletterClick
├── id: UUID (Primary Key)
├── issue: ForeignKey(NewsletterIssue)
├── subscriber: ForeignKey(NewsletterSubscriber)
├── url: URLField
├── clicked_at: DateTimeField (auto_now_add)
├── ip_address: GenericIPAddressField
├── user_agent: CharField (max 300)
└── Indexes: issue, subscriber, clicked_at
```

### Advertisements

#### Advertisement Model
```
Advertisement
├── id: UUID (Primary Key)
├── name: CharField (max 100)
├── advertiser: ForeignKey(User, related_name='advertisements')
├── title: CharField (max 100)
├── description: TextField
├── image: ImageField (R2, nullable)
├── ad_code: TextField (HTML/JavaScript for custom ads)
├── placement: CharField (header, sidebar, footer, in-article)
├── type: CharField (banner, text, image, code)
├── url: URLField (nullable - for clickable ads)
├── target_category: ForeignKey(Category, nullable)
├── start_date: DateField
├── end_date: DateField
├── is_active: Boolean (default: True)
├── impressions: PositiveIntegerField (cached)
├── clicks: PositiveIntegerField (cached)
├── ctr: DecimalField (click-through rate, calculated)
├── budget: DecimalField (for paid campaigns)
├── spent: DecimalField (calculated)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: advertiser, placement, is_active, start_date
             end_date, target_category, created_at
```

#### AdImpression Model
```
AdImpression
├── id: UUID (Primary Key)
├── advertisement: ForeignKey(Advertisement)
├── user: ForeignKey(User, nullable)
├── session_id: CharField (for anonymous)
├── post: ForeignKey(Post, nullable)
├── ip_address: GenericIPAddressField
├── user_agent: CharField (max 300)
├── impressed_at: DateTimeField (auto_now_add)
├── country: CharField (geo-location)
└── Indexes: advertisement, user, session_id, impressed_at
    Retention: 90 days
```

#### AdClick Model
```
AdClick
├── id: UUID (Primary Key)
├── advertisement: ForeignKey(Advertisement)
├── user: ForeignKey(User, nullable)
├── session_id: CharField (for anonymous)
├── post: ForeignKey(Post, nullable)
├── ip_address: GenericIPAddressField
├── user_agent: CharField (max 300)
├── referrer: URLField (nullable)
├── clicked_at: DateTimeField (auto_now_add)
├── country: CharField (geo-location)
└── Indexes: advertisement, user, session_id, clicked_at
```

### Affiliate System

#### AffiliateLink Model
```
AffiliateLink
├── id: UUID (Primary Key)
├── author: ForeignKey(Author, nullable)
├── post: ForeignKey(Post, nullable)
├── platform: CharField (amazon, hostinger, digitalocean, etc.)
├── affiliate_id: CharField
├── title: CharField (max 100)
├── description: TextField (nullable)
├── url: URLField (original affiliate URL)
├── shortened_url: CharField (our tracking URL)
├── tracking_code: CharField (unique)
├── target_category: ForeignKey(Category, nullable)
├── is_active: Boolean (default: True)
├── clicks: PositiveIntegerField (default: 0, cached)
├── conversions: PositiveIntegerField (default: 0, cached)
├── revenue: DecimalField (tracked from platform)
├── commission_rate: DecimalField (percentage)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: tracking_code, platform, is_active, created_at
    Unique Constraint: tracking_code
```

#### AffiliateClick Model
```
AffiliateClick
├── id: UUID (Primary Key)
├── link: ForeignKey(AffiliateLink)
├── user: ForeignKey(User, nullable)
├── session_id: CharField (for anonymous)
├── post: ForeignKey(Post)
├── referrer: URLField
├── ip_address: GenericIPAddressField
├── user_agent: CharField (max 300)
├── country: CharField
├── clicked_at: DateTimeField (auto_now_add)
├── converted: Boolean (default: False)
├── conversion_amount: DecimalField (nullable)
├── conversion_date: DateTimeField (nullable)
└── Indexes: link, user, session_id, clicked_at, converted
    Retention: 2 years (for tracking conversions)
```

### Sponsored Content

#### Sponsorship Model
```
Sponsorship
├── id: UUID (Primary Key)
├── sponsor: ForeignKey(User)
├── company_name: CharField (max 100)
├── company_logo: ImageField (R2)
├── company_url: URLField
├── contact_email: EmailField
├── budget: DecimalField
├── spent: DecimalField (default: 0)
├── payment_status: CharField (pending, paid, disputed)
├── start_date: DateField
├── end_date: DateField
├── is_active: Boolean (default: True)
├── terms: TextField (agreement details)
├── payment_method: CharField (stripe, paypal, bank_transfer)
├── invoice_url: URLField (nullable)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: sponsor, is_active, start_date, end_date
    Unique Constraint: None (allow multiple sponsorships)
```

#### SponsoredCampaign Model
```
SponsoredCampaign
├── id: UUID (Primary Key)
├── sponsorship: ForeignKey(Sponsorship)
├── post: ForeignKey(Post)
├── placement: CharField (featured, sidebar, widget)
├── start_date: DateField
├── end_date: DateField
├── impressions: PositiveIntegerField (cached)
├── clicks: PositiveIntegerField (cached)
├── ctr: DecimalField (calculated)
├── cost: DecimalField (allocated from sponsorship budget)
├── created_at: DateTimeField (auto_now_add)
└── Indexes: sponsorship, post, start_date, end_date
```

### Analytics

#### PageView Model
```
PageView
├── id: UUID (Primary Key)
├── user: ForeignKey(User, nullable)
├── session_id: CharField (for anonymous)
├── page_url: URLField
├── page_title: CharField
├── referrer: URLField (nullable)
├── ip_address: GenericIPAddressField
├── country: CharField (geo-IP)
├── city: CharField
├── device_type: CharField (desktop, mobile, tablet)
├── browser: CharField
├── os: CharField
├── utm_source: CharField (nullable)
├── utm_medium: CharField (nullable)
├── utm_campaign: CharField (nullable)
├── utm_content: CharField (nullable)
├── utm_term: CharField (nullable)
├── viewed_at: DateTimeField (auto_now_add)
└── Indexes: session_id, page_url, viewed_at, utm_source
    Retention: 365 days (older data archived or aggregated)
```

#### DailyAnalytics Model
```
DailyAnalytics (Pre-aggregated)
├── id: UUID (Primary Key)
├── date: DateField (unique)
├── total_pageviews: PositiveIntegerField
├── total_users: PositiveIntegerField
├── total_sessions: PositiveIntegerField
├── bounce_rate: DecimalField
├── avg_session_duration: PositiveIntegerField (seconds)
├── top_pages: JSONField (array of top pages with counts)
├── top_referrers: JSONField (array of top referrers)
├── device_breakdown: JSONField (desktop%, mobile%, tablet%)
├── country_breakdown: JSONField (geo distribution)
├── created_at: DateTimeField (auto_now_add)
└── Indexes: date
    Unique Constraint: date
    Retention: 5 years
```

### Contact & Support

#### ContactMessage Model
```
ContactMessage
├── id: UUID (Primary Key)
├── name: CharField (max 100)
├── email: EmailField
├── subject: CharField (max 200)
├── message: TextField
├── category: CharField (inquiry, support, feedback, other)
├── status: CharField (new, in-progress, resolved)
├── assigned_to: ForeignKey(User, nullable - admin)
├── response: TextField (nullable)
├── responded_at: DateTimeField (nullable)
├── is_spam: Boolean (default: False)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Indexes: email, status, category, created_at
    Retention: 2 years
```

### Website Settings

#### SiteSettings Model
```
SiteSettings (Singleton pattern - only one record)
├── id: UUID (Primary Key)
├── site_name: CharField (default: TechSphere)
├── site_url: URLField
├── site_description: TextField (max 160 chars - for meta description)
├── site_logo: ImageField (R2)
├── favicon: ImageField (R2)
├── owner_email: EmailField
├── owner_name: CharField
├── owner_bio: TextField
├── twitter_handle: CharField
├── facebook_url: URLField (nullable)
├── linkedin_url: URLField (nullable)
├── github_url: URLField (nullable)
├── youtube_url: URLField (nullable)
├── google_analytics_id: CharField (nullable)
├── google_adsense_id: CharField (nullable, sensitive)
├── google_adsense_pub_id: CharField (nullable)
├── sentry_dsn: CharField (nullable, sensitive)
├── support_email: EmailField
├── privacy_policy: TextField (HTML)
├── terms_conditions: TextField (HTML)
├── disclaimer: TextField (HTML)
├── copyright_text: CharField
├── contact_form_enabled: Boolean (default: True)
├── newsletter_enabled: Boolean (default: True)
├── comments_enabled: Boolean (default: True)
├── social_sharing_enabled: Boolean (default: True)
├── maintenance_mode: Boolean (default: False)
├── maintenance_message: CharField (nullable)
├── updated_at: DateTimeField (auto_now)
└── Indexes: None (only one record)
    Unique Constraint: (always 1 record via save override)
```

#### SiteMenu Model
```
SiteMenu
├── id: UUID (Primary Key)
├── name: CharField (max 50 - main, footer, etc.)
├── items: JSONField (hierarchical menu structure)
│   ├── label: String
│   ├── url: String
│   ├── icon: String (FontAwesome)
│   ├── children: Array (for nested items)
├── created_at: DateTimeField (auto_now_add)
├── updated_at: DateTimeField (auto_now)
└── Unique Constraint: name
```

## Database Relationships Summary

```
User (1) ──────────── (1) UserProfile
  │
  ├─ (1) ──────────── (1) Author
  │       │
  │       └─ (1) ──────────── (M) Post
  │              │
  │              ├─ (M) ──────────── (M) Tag
  │              ├─ (1) ──────────── (M) Category
  │              ├─ (1) ──────────── (M) PostView
  │              ├─ (M) ──────────── (M) PostLike (User)
  │              ├─ (M) ──────────── (M) PostBookmark (User)
  │              └─ (1) ──────────── (M) Comment
  │
  ├─ (M) ──────────── (M) Comment (author)
  │       │
  │       └─ (M) ──────────── (M) CommentLike (user)
  │
  ├─ (M) ──────────── (M) PostLike
  ├─ (M) ──────────── (M) PostBookmark
  ├─ (M) ──────────── (1) ReadingHistory
  ├─ (M) ──────────── (1) NewsletterSubscriber
  ├─ (M) ──────────── (1) Advertisement
  ├─ (M) ──────────── (1) Sponsorship
  └─ (M) ──────────── (1) PageView

Post (M) ──────────── (M) Tag
Post (M) ──────────── (1) Category

Newsletter (1) ──────────── (M) NewsletterSubscriber
  │
  └─ (1) ──────────── (M) NewsletterIssue
         │
         └─ (M) ──────────── (M) NewsletterClick (subscriber)

Advertisement (M) ──────────── (M) AdImpression (user)
Advertisement (M) ──────────── (M) AdClick (user)

AffiliateLink (1) ──────────── (M) AffiliateClick (user)
Post (1) ──────────── (M) AffiliateClick

Sponsorship (1) ──────────── (M) SponsoredCampaign
SponsoredCampaign (M) ──────────── (1) Post
```

## Database Optimization Strategies

### Indexes
```
High-volume read queries:
- Post: (status, published_at, is_featured)
- PostView: (post_id, viewed_at)
- Comment: (post_id, is_approved, created_at)
- PageView: (session_id, viewed_at)

Search queries:
- Post: Full-text index on (title, excerpt, content)
- Tag: Index on name and slug
- Category: Index on name and slug

Joins:
- Foreign key indexes (auto-created)
- (author_id, created_at) composite indexes
```

### Query Optimization
```
N+1 Problem Solutions:
- Use select_related() for ForeignKey lookups
- Use prefetch_related() for ManyToMany lookups
- Implement custom Prefetch objects for complex queries

Caching:
- Cache category and tag lists (1 day TTL)
- Cache popular posts (1 hour TTL)
- Cache author profiles (1 day TTL)
- Cache site settings (24 hours TTL)
```

### Database Partitioning Strategy
```
For high-volume tables:
- PostView: Partition by date (monthly partitions)
- PageView: Partition by date (monthly partitions)
- AdImpression: Partition by date (monthly partitions)

Archiving:
- Move data > 1 year to archive tables
- Create views for transparent queries
- Neon handles partitioning automatically
```

## Data Retention Policy

```
Real-time data (7 days):
- PostView detail records
- AdImpression detail records
- PageView detail records

Analytics data (90 days):
- Individual view records
- Click tracking
- Newsletter metrics

Historical data (1 year):
- AffiliateClick (conversion tracking)
- All major events and actions
- PageView aggregated data

Archive (2 years):
- Contact messages
- Old analytics aggregations
- Historical reports

Permanent (indefinite):
- Posts and blog content
- User accounts (soft-delete only)
- Settings and configuration
```

## Migration Strategy

```
Create all models with:
1. Backward-compatible field additions
2. Default values for new required fields
3. No destructive migrations
4. Data migrations for complex changes
5. Rollback procedures documented

Django migration files:
- Numbered sequence (0001, 0002, etc.)
- Reversible where possible
- Tested on staging first
```

This comprehensive schema provides:
- Scalability for millions of posts and users
- Complete audit trails
- Flexible monetization options
- Robust analytics
- User engagement features
- SEO optimization
- Performance optimization through indexing and caching

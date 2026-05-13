-- Maestro CDP Seed Tables
-- Lakebase (managed PostgreSQL) on Databricks
-- Database: maestro_cdp
-- NOTE: journey_state and decisions tables already exist. Do NOT recreate them.

-- ============================================================
-- 1. customers
-- ============================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id   VARCHAR(64)  PRIMARY KEY,
    name          VARCHAR(128) NOT NULL,
    email         VARCHAR(255),
    pet_name      VARCHAR(64),
    pet_type      VARCHAR(64),
    timezone      VARCHAR(64)  DEFAULT 'America/New_York',
    preferred_channel VARCHAR(20) DEFAULT 'email',
    consent_email BOOLEAN      DEFAULT TRUE,
    consent_sms   BOOLEAN      DEFAULT FALSE,
    is_repeat_buyer BOOLEAN    DEFAULT FALSE,
    loyalty_tier  VARCHAR(20)  DEFAULT 'standard',
    quiet_hours_start INT      DEFAULT 21,
    quiet_hours_end   INT      DEFAULT 7,
    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

-- ============================================================
-- 2. orders (carts: abandoned, completed, pending)
-- ============================================================
CREATE TABLE IF NOT EXISTS orders (
    order_id    VARCHAR(64)  PRIMARY KEY,
    customer_id VARCHAR(64)  NOT NULL,
    status      VARCHAR(20)  DEFAULT 'abandoned',
    total       DECIMAL(10,2),
    created_at  TIMESTAMPTZ  DEFAULT NOW(),
    abandoned_at TIMESTAMPTZ
);

-- ============================================================
-- 3. order_items
-- ============================================================
CREATE TABLE IF NOT EXISTS order_items (
    item_id    SERIAL       PRIMARY KEY,
    order_id   VARCHAR(64)  NOT NULL,
    product_id VARCHAR(64)  NOT NULL,
    qty        INT          DEFAULT 1,
    price      DECIMAL(10,2)
);

-- ============================================================
-- 4. production_calendar
-- ============================================================
CREATE TABLE IF NOT EXISTS production_calendar (
    product_id      VARCHAR(64)  PRIMARY KEY,
    product_name    VARCHAR(256),
    production_days INT          DEFAULT 5,
    shipping_method VARCHAR(64)  DEFAULT 'standard',
    is_available    BOOLEAN      DEFAULT TRUE
);

-- ============================================================
-- 5. campaigns
-- ============================================================
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id   VARCHAR(64)  PRIMARY KEY,
    name          VARCHAR(256) NOT NULL,
    campaign_type VARCHAR(64),
    status        VARCHAR(20)  DEFAULT 'active',
    scheduled_send TIMESTAMPTZ,
    channel       VARCHAR(20)  DEFAULT 'email',
    created_at    TIMESTAMPTZ  DEFAULT NOW()
);

-- ============================================================
-- 6. campaign_membership
-- ============================================================
CREATE TABLE IF NOT EXISTS campaign_membership (
    id          SERIAL       PRIMARY KEY,
    campaign_id VARCHAR(64)  NOT NULL,
    customer_id VARCHAR(64)  NOT NULL,
    enrolled_at TIMESTAMPTZ  DEFAULT NOW(),
    UNIQUE(campaign_id, customer_id)
);

-- ============================================================
-- 7. support_tickets
-- ============================================================
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id   VARCHAR(64)  PRIMARY KEY,
    customer_id VARCHAR(64)  NOT NULL,
    subject     VARCHAR(256),
    status      VARCHAR(20)  DEFAULT 'open',
    priority    VARCHAR(20)  DEFAULT 'medium',
    created_at  TIMESTAMPTZ  DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ============================================================
-- 8. consent
-- ============================================================
CREATE TABLE IF NOT EXISTS consent (
    customer_id       VARCHAR(64) PRIMARY KEY,
    email             BOOLEAN     DEFAULT TRUE,
    sms               BOOLEAN     DEFAULT FALSE,
    push              BOOLEAN     DEFAULT FALSE,
    quiet_hours_start INT         DEFAULT 21,
    quiet_hours_end   INT         DEFAULT 7,
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 9. propensity_scores (cached model outputs)
-- ============================================================
CREATE TABLE IF NOT EXISTS propensity_scores (
    id            SERIAL       PRIMARY KEY,
    customer_id   VARCHAR(64)  NOT NULL,
    intent        VARCHAR(64)  NOT NULL,
    score         DECIMAL(5,4),
    model_version VARCHAR(64),
    confidence    DECIMAL(5,4),
    scored_at     TIMESTAMPTZ  DEFAULT NOW(),
    UNIQUE(customer_id, intent)
);


-- ============================================================
-- 10. sent_emails (Beat 3 — simulated email delivery tracking)
-- ============================================================
CREATE TABLE IF NOT EXISTS sent_emails (
    email_id      VARCHAR(64)  PRIMARY KEY,
    journey_id    VARCHAR(64)  NOT NULL,
    customer_id   VARCHAR(64)  NOT NULL,
    subject       VARCHAR(512) NOT NULL,
    body_html     TEXT         NOT NULL,
    channel       VARCHAR(20)  DEFAULT 'email',
    status        VARCHAR(20)  DEFAULT 'delivered',
    sent_at       TIMESTAMPTZ  DEFAULT NOW()
);


-- ============================================================
-- SEED DATA
-- ============================================================

-- ---------- customers ----------
INSERT INTO customers (customer_id, name, email, pet_name, pet_type, timezone, preferred_channel, consent_email, consent_sms, is_repeat_buyer, loyalty_tier, quiet_hours_start, quiet_hours_end)
VALUES
    ('cust_88241', 'Cindy Chen',   'cindy.chen@example.com',   'Whiskers', 'tabby kitten',   'America/Chicago',      'email', TRUE,  FALSE, TRUE,  'gold',     21, 7),
    ('cust_10042', 'Dave Miller',  'dave.miller@example.com',  NULL,       NULL,              'America/New_York',     'email', TRUE,  FALSE, FALSE, 'standard', 21, 7),
    ('cust_55319', 'Maria Santos', 'maria.santos@example.com', 'Luna',     'golden retriever','America/Los_Angeles',  'email', TRUE,  TRUE,  TRUE,  'vip',      22, 8),
    ('cust_77120', 'James Park',   'james.park@example.com',   'Shadow',   'black cat',       'America/New_York',     'email', TRUE,  FALSE, FALSE, 'standard', 21, 7),
    ('cust_33456', 'Aisha Patel',  'aisha.patel@example.com',  NULL,       NULL,              'America/Chicago',      'email', TRUE,  FALSE, TRUE,  'gold',     21, 7),
    ('cust_99001', 'Tom Bradley',  'tom.bradley@example.com',  NULL,       NULL,              'America/Denver',       'email', FALSE, FALSE, TRUE,  'gold',     22, 8)
ON CONFLICT (customer_id) DO NOTHING;

-- ---------- orders ----------
INSERT INTO orders (order_id, customer_id, status, total, created_at, abandoned_at)
VALUES
    -- Cindy: abandoned cart
    ('cart_77a3f', 'cust_88241', 'abandoned',  42.00, '2026-05-09T19:45:00-05:00', '2026-05-09T20:18:00-05:00'),
    -- Dave: no cart (clean new customer)
    -- Maria: completed order + new pending cart
    ('ord_m5501',  'cust_55319', 'completed', 128.50, '2026-04-28T14:30:00-07:00', NULL),
    ('cart_m5502', 'cust_55319', 'abandoned',  65.00, '2026-05-09T11:05:00-07:00', '2026-05-09T11:42:00-07:00'),
    -- James: completed order from months ago
    ('ord_j7701',  'cust_77120', 'completed',  34.99, '2026-02-14T10:00:00-05:00', NULL),
    -- Aisha: high-value abandoned cart
    ('cart_a3301', 'cust_33456', 'abandoned', 280.00, '2026-05-09T17:20:00-05:00', '2026-05-09T18:05:00-05:00'),
    -- Tom: completed order
    ('ord_t9901',  'cust_99001', 'completed',  55.00, '2026-05-01T09:15:00-06:00', NULL)
ON CONFLICT (order_id) DO NOTHING;

-- ---------- order_items ----------
INSERT INTO order_items (order_id, product_id, qty, price)
VALUES
    -- Cindy's abandoned cart
    ('cart_77a3f', 'pb_welcome_home_24pp', 1, 42.00),
    -- Maria's completed order
    ('ord_m5501',  'canvas_16x20',        1, 89.00),
    ('ord_m5501',  'mug_custom_11oz',     2, 19.75),
    -- Maria's abandoned cart
    ('cart_m5502', 'pb_travel_36pp',       1, 65.00),
    -- James's old completed order
    ('ord_j7701',  'ornament_round_3in',   1, 34.99),
    -- Aisha's high-value abandoned cart
    ('cart_a3301', 'canvas_24x36',         1, 149.00),
    ('cart_a3301', 'pb_premium_48pp',      1,  89.00),
    ('cart_a3301', 'prints_5x7_pack10',    1,  42.00),
    -- Tom's completed order
    ('ord_t9901',  'calendar_wall_12mo',   1,  55.00)
ON CONFLICT DO NOTHING;

-- ---------- production_calendar ----------
INSERT INTO production_calendar (product_id, product_name, production_days, shipping_method, is_available)
VALUES
    ('pb_welcome_home_24pp', 'Welcome Home Photo Book 24pp',      4, 'standard',  TRUE),
    ('pb_travel_36pp',       'Travel Memories Photo Book 36pp',    5, 'standard',  TRUE),
    ('pb_premium_48pp',      'Premium Photo Book 48pp',            6, 'standard',  TRUE),
    ('canvas_16x20',         'Canvas Print 16x20',                 3, 'standard',  TRUE),
    ('canvas_24x36',         'Canvas Print 24x36',                 4, 'standard',  TRUE),
    ('mug_custom_11oz',      'Custom Photo Mug 11oz',              2, 'standard',  TRUE),
    ('ornament_round_3in',   'Round Photo Ornament 3in',           3, 'standard',  FALSE),  -- seasonal, out of stock
    ('prints_5x7_pack10',    'Photo Prints 5x7 Pack of 10',       1, 'standard',  TRUE),
    ('calendar_wall_12mo',   'Wall Calendar 12-Month',             3, 'standard',  TRUE)
ON CONFLICT (product_id) DO NOTHING;

-- ---------- campaigns ----------
INSERT INTO campaigns (campaign_id, name, campaign_type, status, scheduled_send, channel)
VALUES
    ('camp_spring_24',    'Spring Seasonal 2026',         'seasonal',      'active',    '2026-05-10T09:00:00-05:00', 'email'),
    ('camp_cart_recovery','Abandoned Cart Recovery',       'triggered',     'active',    NULL,                         'email'),
    ('camp_vip_loyalty',  'VIP Loyalty Exclusive',         'loyalty',       'paused',    '2026-05-15T10:00:00-05:00', 'email'),
    ('camp_reactivation', 'Win-Back: 90-Day Dormant',      'reactivation',  'active',    '2026-05-12T08:00:00-05:00', 'email'),
    ('camp_summer_prev',  'Summer Preview Collection',     'seasonal',      'active',    '2026-05-20T09:00:00-07:00', 'email'),
    ('camp_mothers_day',  'Mothers Day Gift Guide',        'seasonal',      'completed', '2026-05-08T08:00:00-05:00', 'email'),
    ('camp_flash_sale',   'Flash Sale: 20% Off Canvas',    'promotional',   'active',    '2026-05-11T12:00:00-05:00', 'email'),
    ('camp_referral',     'Refer-a-Friend Spring',         'referral',      'active',    NULL,                         'email')
ON CONFLICT (campaign_id) DO NOTHING;

-- ---------- campaign_membership ----------
INSERT INTO campaign_membership (campaign_id, customer_id)
VALUES
    -- Cindy: 4 campaigns (Spring Seasonal, Cart Recovery, VIP Loyalty, Reactivation)
    ('camp_spring_24',     'cust_88241'),
    ('camp_cart_recovery',  'cust_88241'),
    ('camp_vip_loyalty',    'cust_88241'),
    ('camp_reactivation',   'cust_88241'),
    -- Dave: no campaigns (clean happy path)
    -- Maria: 3 active campaigns (Summer Preview, Flash Sale, Referral)
    ('camp_summer_prev',    'cust_55319'),
    ('camp_flash_sale',     'cust_55319'),
    ('camp_referral',       'cust_55319'),
    -- James: 1 campaign (Reactivation -- lapsed buyer)
    ('camp_reactivation',   'cust_77120'),
    -- Aisha: 2 campaigns (Cart Recovery, Flash Sale) -- near cap
    ('camp_cart_recovery',  'cust_33456'),
    ('camp_flash_sale',     'cust_33456'),
    -- Tom: 1 campaign (Spring Seasonal) -- but consent_email=false so blocked
    ('camp_spring_24',      'cust_99001')
ON CONFLICT (campaign_id, customer_id) DO NOTHING;

-- ---------- support_tickets ----------
-- Cindy: NONE (clean)
-- Dave: NONE (clean new customer)
-- Maria: 1 resolved ticket (positive outcome)
-- James: 1 open complaint (friction scenario)
-- Aisha: NONE
-- Tom: 1 resolved ticket
INSERT INTO support_tickets (ticket_id, customer_id, subject, status, priority, created_at, resolved_at)
VALUES
    ('tkt_m5501', 'cust_55319', 'Shipping delay on canvas order',    'resolved', 'medium', '2026-04-30T09:00:00-07:00', '2026-05-02T14:30:00-07:00'),
    ('tkt_j7701', 'cust_77120', 'Ornament arrived damaged',          'open',     'high',   '2026-02-20T11:00:00-05:00', NULL),
    ('tkt_t9901', 'cust_99001', 'Calendar misprinted month of March','resolved', 'medium', '2026-05-03T08:00:00-06:00', '2026-05-05T16:00:00-06:00')
ON CONFLICT (ticket_id) DO NOTHING;

-- ---------- consent ----------
INSERT INTO consent (customer_id, email, sms, push, quiet_hours_start, quiet_hours_end)
VALUES
    ('cust_88241', TRUE,  FALSE, FALSE, 21, 7),
    ('cust_10042', TRUE,  FALSE, FALSE, 21, 7),
    ('cust_55319', TRUE,  TRUE,  TRUE,  22, 8),
    ('cust_77120', TRUE,  FALSE, FALSE, 21, 7),
    ('cust_33456', TRUE,  FALSE, FALSE, 21, 7),
    ('cust_99001', FALSE, FALSE, FALSE, 22, 8)
ON CONFLICT (customer_id) DO NOTHING;

-- ---------- propensity_scores ----------
INSERT INTO propensity_scores (customer_id, intent, score, model_version, confidence)
VALUES
    -- Cindy: high cart recovery propensity
    ('cust_88241', 'cart_recovery',   0.8100, 'v3', 0.8900),
    -- Dave: moderate browse-to-buy (new customer)
    ('cust_10042', 'browse_to_buy',   0.4200, 'v3', 0.7100),
    -- Maria: high cross-sell, moderate cart recovery
    ('cust_55319', 'cross_sell',      0.7600, 'v3', 0.8500),
    ('cust_55319', 'cart_recovery',   0.6900, 'v3', 0.8200),
    -- James: low reactivation propensity (friction)
    ('cust_77120', 'reactivation',    0.3100, 'v3', 0.6500),
    -- Aisha: very high cart recovery
    ('cust_33456', 'cart_recovery',   0.9200, 'v3', 0.9100),
    -- Tom: moderate loyalty upsell (but consent blocked)
    ('cust_99001', 'loyalty_upsell',  0.5800, 'v3', 0.7400)
ON CONFLICT (customer_id, intent) DO NOTHING;

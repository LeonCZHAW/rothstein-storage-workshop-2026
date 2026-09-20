-- Vollständiges Demoschema; Datenimport getrennt von DDL.
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS posts (
    post_id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    created_at TEXT NOT NULL,
    text TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS likes (
    like_id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(post_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    created_at TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS comments (
    comment_id INTEGER PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES posts(post_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    created_at TEXT NOT NULL,
    text TEXT NOT NULL
) STRICT;
CREATE TABLE IF NOT EXISTS follows (
    src_user_id INTEGER NOT NULL REFERENCES users(user_id),
    dst_user_id INTEGER NOT NULL REFERENCES users(user_id),
    since TEXT NOT NULL,
    PRIMARY KEY (src_user_id, dst_user_id),
    CHECK (src_user_id <> dst_user_id)
) STRICT;
CREATE INDEX IF NOT EXISTS idx_posts_user_created ON posts(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_likes_post ON likes(post_id);
CREATE INDEX IF NOT EXISTS idx_comments_post ON comments(post_id);
CREATE INDEX IF NOT EXISTS idx_follows_dst ON follows(dst_user_id);

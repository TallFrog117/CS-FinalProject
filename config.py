# config.py
# ──────────────────────────────────────────────
#  General engine settings.
#  Your MySQL password lives in db_credentials.py,
#  NOT here — edit that file instead, and this file
#  can be freely replaced/updated without ever
#  touching your saved password.
# ──────────────────────────────────────────────

from db_credentials import DB_USER, DB_PASSWORD

DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "user":     DB_USER,
    "password": DB_PASSWORD,
    "database": "physics_engine"
}

# ── Window ──────────────────────────────────────
WINDOW_WIDTH  = 1920
WINDOW_HEIGHT = 1080
FPS           = 60
WINDOW_TITLE  = "2D Physics Engine"

# ── Physics ─────────────────────────────────────
MAX_DT           = 1 / 30.0   # cap delta-time to avoid instability
PHYSICS_SUBSTEPS = 4          # mini-steps per rendered frame — raise for
                               # more accurate/stable collisions (try 4-8),
                               # lower (1) for max performance on weak machines
POSITION_SLOP    = 0.5        # penetration allowance before correction (px)
POSITION_PERCENT = 0.4        # how much of penetration to correct per step
VELOCITY_SLEEP   = 2.0        # px/s below which body can "sleep" (future use)

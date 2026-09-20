-- ============================================================
--  Physics Engine Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS physics_engine;
USE physics_engine;

-- -----------------------------------------------------------
-- simulations: one row per named preset / run
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS simulations (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL,
    gravity     FLOAT           NOT NULL DEFAULT 980.0,   -- pixels/s^2 (980 ≈ 9.8 m/s² scaled)
    created_at  TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- -----------------------------------------------------------
-- objects: one row per physics body in a simulation
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS objects (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    simulation_id   INT             NOT NULL,
    label           VARCHAR(50)     NOT NULL DEFAULT 'object',

    -- shape: 'circle' or 'rect'
    shape           ENUM('circle','rect') NOT NULL DEFAULT 'circle',

    -- physical properties
    mass            FLOAT           NOT NULL DEFAULT 1.0,       -- kg
    restitution     FLOAT           NOT NULL DEFAULT 0.6,       -- 0 = no bounce, 1 = perfect bounce
    friction_coeff  FLOAT           NOT NULL DEFAULT 0.3,       -- kinetic friction μk

    -- initial state
    pos_x           FLOAT           NOT NULL DEFAULT 400.0,     -- pixels
    pos_y           FLOAT           NOT NULL DEFAULT 100.0,
    vel_x           FLOAT           NOT NULL DEFAULT 0.0,       -- pixels/s
    vel_y           FLOAT           NOT NULL DEFAULT 0.0,

    -- shape dimensions
    radius          FLOAT           DEFAULT 25.0,               -- circles only
    width           FLOAT           DEFAULT 50.0,               -- rects only
    height          FLOAT           DEFAULT 50.0,               -- rects only

    -- colour (hex string e.g. '#FF5733')
    color           VARCHAR(10)     DEFAULT '#FFFFFF',

    -- static bodies never move (floors, walls)
    is_static       BOOLEAN         NOT NULL DEFAULT FALSE,

    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
);

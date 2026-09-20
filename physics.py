# physics.py
# ──────────────────────────────────────────────
#  Core physics engine:
#   • Force application (gravity, friction)
#   • Collision detection (circle-circle,
#     AABB-AABB, circle-AABB)
#   • Collision resolution (impulse + positional
#     correction)
# ──────────────────────────────────────────────

import math
from dataclasses import dataclass, field
from typing import List, Optional

from vector2   import Vector2
from rigidbody import RigidBody
from config    import (
    POSITION_SLOP,
    POSITION_PERCENT,
    MAX_DT,
)


# ── Collision manifold ───────────────────────────────────────────────────────

@dataclass
class Manifold:
    """Stores all data about one collision between two bodies."""
    a:          RigidBody
    b:          RigidBody
    normal:     Vector2 = field(default_factory=Vector2.zero)
    penetration: float  = 0.0
    has_contact: bool   = False


# ── Physics world ────────────────────────────────────────────────────────────

class PhysicsWorld:
    def __init__(self, gravity: float = 980.0, substeps: int = 4):
        """
        gravity  — downward acceleration in pixels/s²
                   (980 ≈ real 9.8 m/s² at 100 px = 1 m scale)
        substeps — how many mini-physics-steps to run per rendered frame.
                   Higher = more accurate collisions and less tunneling
                   through thin/fast objects, at the cost of CPU time.
                   1 = original behaviour. 4-8 is a good quality boost.
        """
        self.gravity   = Vector2(0, gravity)
        self.bodies:   List[RigidBody] = []
        self.substeps  = max(1, substeps)

    def add_body(self, body: RigidBody):
        self.bodies.append(body)

    def remove_body(self, body: RigidBody):
        self.bodies.remove(body)

    def clear(self):
        self.bodies.clear()

    # ── Main step ────────────────────────────────
    def step(self, dt: float):
        """
        Called once per rendered frame. Internally runs `self.substeps`
        smaller physics updates so collisions are resolved more precisely
        than the visual frame rate alone would allow.
        """
        dt = min(dt, MAX_DT)
        sub_dt = dt / self.substeps

        for _ in range(self.substeps):
            self._substep(sub_dt)

    def _substep(self, dt: float):
        # 1. Apply forces (gravity + friction pre-pass)
        for body in self.bodies:
            self._apply_gravity(body)

        # 2. Broad-phase + narrow-phase collision
        manifolds = self._detect_collisions()

        # 3. Resolve collisions (impulse)
        for m in manifolds:
            self._resolve_impulse(m)

        # 4. Positional correction (prevent sinking)
        for m in manifolds:
            self._positional_correction(m)

        # 5. Apply friction along contact tangent
        for m in manifolds:
            self._apply_friction(m)

        # 6. Integrate all bodies
        for body in self.bodies:
            body.integrate(dt)

    # ── Forces ──────────────────────────────────

    def _apply_gravity(self, body: RigidBody):
        if body.is_static:
            return
        # F = m * g
        body.apply_force(self.gravity * body.mass)

    # ── Collision detection ──────────────────────

    def _detect_collisions(self) -> List[Manifold]:
        manifolds = []
        n = len(self.bodies)
        for i in range(n):
            for j in range(i + 1, n):
                a = self.bodies[i]
                b = self.bodies[j]

                # Skip pairs where both are static
                if a.is_static and b.is_static:
                    continue

                # Broad phase
                if not a.aabb_overlaps(b):
                    continue

                # Narrow phase
                m = self._narrow_phase(a, b)
                if m and m.has_contact:
                    manifolds.append(m)

        return manifolds

    def _narrow_phase(self, a: RigidBody, b: RigidBody) -> Optional[Manifold]:
        if a.shape == "circle" and b.shape == "circle":
            return self._circle_vs_circle(a, b)
        elif a.shape == "rect" and b.shape == "rect":
            return self._aabb_vs_aabb(a, b)
        elif a.shape == "circle" and b.shape == "rect":
            return self._circle_vs_aabb(a, b)
        elif a.shape == "rect" and b.shape == "circle":
            m = self._circle_vs_aabb(b, a)
            if m:
                m.normal = -m.normal   # flip normal since we swapped order
            return m
        return None

    # ── Circle vs Circle ────────────────────────
    def _circle_vs_circle(self, a: RigidBody, b: RigidBody) -> Manifold:
        m = Manifold(a, b)
        diff = b.position - a.position
        dist_sq = diff.length_sq()
        radii   = a.radius + b.radius

        if dist_sq >= radii * radii:
            return m  # no contact

        dist = math.sqrt(dist_sq)
        m.has_contact = True

        if dist < 1e-6:
            # Exactly overlapping — push apart on arbitrary axis
            m.normal      = Vector2(1, 0)
            m.penetration = radii
        else:
            m.normal      = diff / dist        # unit vector a→b
            m.penetration = radii - dist

        return m

    # ── AABB vs AABB ────────────────────────────
    def _aabb_vs_aabb(self, a: RigidBody, b: RigidBody) -> Manifold:
        m = Manifold(a, b)
        diff = b.position - a.position

        overlap_x = (a.half_w + b.half_w) - abs(diff.x)
        overlap_y = (a.half_h + b.half_h) - abs(diff.y)

        if overlap_x <= 0 or overlap_y <= 0:
            return m  # separating axis found

        m.has_contact = True

        # Push along the axis with the smallest overlap
        if overlap_x < overlap_y:
            m.normal      = Vector2(1, 0) if diff.x > 0 else Vector2(-1, 0)
            m.penetration = overlap_x
        else:
            m.normal      = Vector2(0, 1) if diff.y > 0 else Vector2(0, -1)
            m.penetration = overlap_y

        return m

    # ── Circle vs AABB ──────────────────────────
    def _circle_vs_aabb(self, circle: RigidBody, rect: RigidBody) -> Manifold:
        m = Manifold(circle, rect)

        # Clamp circle centre to rect's extents → find closest point on rect
        diff    = circle.position - rect.position
        clamped = Vector2(
            max(-rect.half_w, min(diff.x, rect.half_w)),
            max(-rect.half_h, min(diff.y, rect.half_h)),
        )

        inside = False

        # If circle centre is inside the rect, push it to the nearest edge
        if diff.x == clamped.x and diff.y == clamped.y:
            inside = True
            if abs(diff.x) > abs(diff.y):
                clamped.x = rect.half_w if clamped.x > 0 else -rect.half_w
            else:
                clamped.y = rect.half_h if clamped.y > 0 else -rect.half_h

        closest = rect.position + clamped
        sep     = circle.position - closest
        dist_sq = sep.length_sq()

        if not inside and dist_sq >= circle.radius * circle.radius:
            return m  # no contact

        dist = math.sqrt(dist_sq) if dist_sq > 1e-12 else 0.0

        m.has_contact = True
        if dist < 1e-6:
            m.normal      = Vector2(0, -1)
            m.penetration = circle.radius
        else:
            m.normal      = sep / dist
            m.penetration = circle.radius - dist
            if not inside:
                m.normal = -m.normal

        return m

    # ── Impulse resolution ───────────────────────
    def _resolve_impulse(self, m: Manifold):
        a, b = m.a, m.b

        # Relative velocity along contact normal
        rel_vel = b.velocity - a.velocity
        vel_along_normal = rel_vel.dot(m.normal)

        # Don't resolve if objects are separating
        if vel_along_normal > 0:
            return

        e = min(a.restitution, b.restitution)

        # Impulse scalar
        j = -(1 + e) * vel_along_normal
        j /= (a.inv_mass + b.inv_mass)

        impulse = m.normal * j

        if not a.is_static:
            a.velocity -= impulse * a.inv_mass
        if not b.is_static:
            b.velocity += impulse * b.inv_mass

    # ── Friction ─────────────────────────────────
    def _apply_friction(self, m: Manifold):
        a, b = m.a, m.b

        rel_vel = b.velocity - a.velocity

        # Tangent vector (perpendicular to normal)
        dot_n   = rel_vel.dot(m.normal)
        tangent = rel_vel - m.normal * dot_n
        if tangent.length_sq() < 1e-12:
            return
        tangent.normalize()

        # Friction impulse magnitude
        jt = -rel_vel.dot(tangent)
        jt /= (a.inv_mass + b.inv_mass)

        # Coulomb's law: clamp to μ * normal impulse
        mu = (a.friction_coeff + b.friction_coeff) * 0.5

        # Approximate normal impulse from restitution step
        e        = min(a.restitution, b.restitution)
        vel_n    = (b.velocity - a.velocity).dot(m.normal)
        j_normal = abs(-(1 + e) * vel_n / (a.inv_mass + b.inv_mass))

        friction_impulse: Vector2
        if abs(jt) < j_normal * mu:
            friction_impulse = tangent * jt
        else:
            friction_impulse = tangent * (-j_normal * mu)

        if not a.is_static:
            a.velocity -= friction_impulse * a.inv_mass
        if not b.is_static:
            b.velocity += friction_impulse * b.inv_mass

    # ── Positional correction (Baumgarte) ────────
    def _positional_correction(self, m: Manifold):
        a, b = m.a, m.b

        correction_mag = (
            max(m.penetration - POSITION_SLOP, 0.0)
            / (a.inv_mass + b.inv_mass)
            * POSITION_PERCENT
        )
        correction = m.normal * correction_mag

        if not a.is_static:
            a.position -= correction * a.inv_mass
        if not b.is_static:
            b.position += correction * b.inv_mass

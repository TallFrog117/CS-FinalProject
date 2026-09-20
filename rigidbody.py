# rigidbody.py
# ──────────────────────────────────────────────
#  Represents a single physics object.
#  Supports two shapes: 'circle' and 'rect'.
# ──────────────────────────────────────────────

from vector2 import Vector2


class RigidBody:
    def __init__(
        self,
        label:          str     = "body",
        shape:          str     = "circle",   # 'circle' | 'rect'
        mass:           float   = 1.0,
        restitution:    float   = 0.6,
        friction_coeff: float   = 0.3,
        position:       Vector2 = None,
        velocity:       Vector2 = None,
        radius:         float   = 25.0,       # circles
        width:          float   = 50.0,       # rects
        height:         float   = 50.0,       # rects
        color:          str     = "#FFFFFF",
        is_static:      bool    = False,
        body_id:        int     = -1,
    ):
        self.label          = label
        self.shape          = shape
        self.restitution    = restitution
        self.friction_coeff = friction_coeff
        self.color          = color
        self.is_static      = is_static
        self.body_id        = body_id

        # Static bodies have infinite mass → inv_mass = 0
        self.mass    = mass if not is_static else float("inf")
        self.inv_mass = 0.0 if is_static else (1.0 / mass if mass > 0 else 0.0)

        # Kinematics
        self.position     = position.copy() if position else Vector2(0, 0)
        self.velocity     = velocity.copy() if velocity else Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        # Accumulated force this frame
        self._force = Vector2(0, 0)

        # Shape dimensions
        self.radius = radius
        self.width  = width
        self.height = height

    # ── Force accumulation ──────────────────────
    def apply_force(self, force: Vector2):
        if not self.is_static:
            self._force += force

    def clear_forces(self):
        self._force = Vector2(0, 0)

    # ── Integration (Semi-implicit Euler) ───────
    def integrate(self, dt: float):
        if self.is_static:
            return

        # a = F / m
        self.acceleration = self._force * self.inv_mass

        # v += a * dt
        self.velocity += self.acceleration * dt

        # x += v * dt
        self.position += self.velocity * dt

        self.clear_forces()

    # ── Bounding-box helpers (for broad phase) ──
    def aabb(self):
        """Return (min_x, min_y, max_x, max_y)."""
        if self.shape == "circle":
            return (
                self.position.x - self.radius,
                self.position.y - self.radius,
                self.position.x + self.radius,
                self.position.y + self.radius,
            )
        else:  # rect — position is centre
            hw = self.width  / 2
            hh = self.height / 2
            return (
                self.position.x - hw,
                self.position.y - hh,
                self.position.x + hw,
                self.position.y + hh,
            )

    def aabb_overlaps(self, other: "RigidBody") -> bool:
        ax1, ay1, ax2, ay2 = self.aabb()
        bx1, by1, bx2, by2 = other.aabb()
        return ax1 < bx2 and ax2 > bx1 and ay1 < by2 and ay2 > by1

    # ── Rect half-extents ────────────────────────
    @property
    def half_w(self):
        return self.width / 2

    @property
    def half_h(self):
        return self.height / 2

    def __repr__(self):
        return (
            f"RigidBody({self.label!r}, shape={self.shape}, "
            f"pos={self.position}, vel={self.velocity})"
        )

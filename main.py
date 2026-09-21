# main.py
# ──────────────────────────────────────────────
#  Entry point for the 2D Physics Engine.
#
#  States
#  ------
#  MENU     — browse / select a simulation preset
#  RUNNING  — active physics simulation
#
#  Controls (in RUNNING state)
#  ---------------------------
#  SPACE    pause / resume
#  R        restart current simulation
#  D        toggle AABB debug boxes
#  V        toggle velocity arrows
#  ESC      return to menu
#  Q        quit
# ──────────────────────────────────────────────

import sys
import pygame

# ── Windows DPI fix ──────────────────────────────
# On Windows, display scaling (125%/150%/etc, common on laptops) can cause
# pygame windows to render smaller than requested or show only part of the
# canvas. Telling Windows this process handles its own scaling fixes it.
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass  # harmless if it fails — just means the OS-scaling fix didn't apply

from config   import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE, MAX_DT, PHYSICS_SUBSTEPS
from database import list_simulations, load_simulation
from physics  import PhysicsWorld
from renderer import Renderer
from vector2  import Vector2


# ── App states ────────────────────────────────
STATE_MENU    = "menu"
STATE_RUNNING = "running"


class PhysicsApp:
    def __init__(self):
        pygame.init()
        self.screen   = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock    = pygame.time.Clock()
        self.renderer = Renderer(self.screen)

        self.state          = STATE_MENU
        self.simulations    = []       # list of dicts from DB
        self.selected_index = 0
        self.sim_info       = {}
        self.world          = PhysicsWorld(substeps=PHYSICS_SUBSTEPS)
        self.paused         = False

        self._load_sim_list()

    # ── DB helpers ────────────────────────────
    def _load_sim_list(self):
        try:
            self.simulations = list_simulations()
        except Exception as e:
            raise RuntimeError(
                f"Could not load simulations from MySQL: {e}\n"
                f"Check: (1) MySQL is running, (2) db_credentials.py has the "
                f"correct password for THIS computer, (3) you've run "
                f"'mysql -u root -p < schema.sql' and '... < seed.sql' here."
            ) from e

        if not self.simulations:
            print("[WARNING] No simulations found in DB. Run seed.sql first.")

    def _load_sim(self, sim_id: int):
        self.sim_info, bodies = load_simulation(sim_id)
        self.world = PhysicsWorld(gravity=float(self.sim_info["gravity"]), substeps=PHYSICS_SUBSTEPS)
        for body in bodies:
            self.world.add_body(body)
        self.paused = False

    # ── Main loop ─────────────────────────────
    def run(self):
        while True:
            if self.state == STATE_MENU:
                self._run_menu()
            elif self.state == STATE_RUNNING:
                self._run_simulation()

    # ── Menu loop ─────────────────────────────
    def _run_menu(self):
        while self.state == STATE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self._quit()

                    elif event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 1)

                    elif event.key == pygame.K_DOWN:
                        self.selected_index = min(
                            len(self.simulations) - 1,
                            self.selected_index + 1,
                        )

                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if self.simulations:
                            sim = self.simulations[self.selected_index]
                            self._load_sim(sim["id"])
                            self.state = STATE_RUNNING

            self.renderer.draw_menu(self.simulations, self.selected_index)
            pygame.display.flip()
            self.clock.tick(FPS)

    # ── Simulation loop ────────────────────────
    def _run_simulation(self):
        while self.state == STATE_RUNNING:
            dt = self.clock.tick(FPS) / 1000.0  # seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._quit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = STATE_MENU

                    elif event.key == pygame.K_q:
                        self._quit()

                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused

                    elif event.key == pygame.K_r:
                        # Reload same simulation from DB
                        self._load_sim(self.sim_info["id"])

                    elif event.key == pygame.K_d:
                        self.renderer.show_debug = not self.renderer.show_debug

                    elif event.key == pygame.K_v:
                        self.renderer.show_vel = not self.renderer.show_vel

            if not self.paused:
                self.world.step(dt)

            self.renderer.draw(
                bodies   = self.world.bodies,
                sim_info = self.sim_info,
                fps      = self.clock.get_fps(),
                paused   = self.paused,
            )
            pygame.display.flip()

    # ── Quit ─────────────────────────────────
    def _quit(self):
        pygame.quit()
        sys.exit(0)


# ── Entry point ──────────────────────────────
if __name__ == "__main__":
    try:
        app = PhysicsApp()
        app.run()
    except Exception:
        import traceback
        print("\n" + "=" * 60)
        print("The program crashed. Full error below:")
        print("=" * 60)
        traceback.print_exc()
        print("=" * 60)
        input("\nPress Enter to close this window...")
        sys.exit(1)

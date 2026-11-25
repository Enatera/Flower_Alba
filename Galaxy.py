import math
import random
import pygame

# --- Configuración de ventana ---
WIDTH, HEIGHT = 900, 950
FPS = 60
TITLE = "Particles Flower"

# --- Paletas de colores inspiradas en la escena ---
LEAF_PAL = [
    (20, 55, 220),
    (35, 95, 255),
    (65, 140, 255),
    (15, 35, 175),
    (95, 175, 255),
]

PETAL_PAL = [
    (25, 60, 235),
    (45, 105, 255),
    (80, 150, 255),
    (120, 110, 255),
    (165, 150, 255),
]

CORE_PAL = [
    (175, 155, 255),
    (210, 195, 255),
    (245, 235, 150),
    (255, 245, 185),
    (140, 175, 255),
]

ORBIT_PAL = [
    (150, 175, 255),
    (195, 210, 255),
    (115, 145, 255),
    (240, 245, 255),
]

GROUND_PAL = [
    (45, 50, 75),
    (75, 85, 120),
    (115, 125, 165),
    (165, 175, 210),
    (30, 34, 52),
]


class Particle:
    def __init__(
        self,
        base_x: float,
        base_y: float,
        color: tuple[int, int, int],
        radius: float = 1.6,
        phase: float = 0.0,
        amp_x: float = 1.5,
        amp_y: float = 1.5,
        speed: float = 2.0,
        sway_factor: float = 0.0,
        kind: str = "body",
        # Parámetros extra para flor animada
        rel_x: float = 0.0,
        rel_y: float = 0.0,
        petal_idx: int = 0,
        u: float = 0.0,
        # Parámetros extra para anillos giratorios
        orbit_center_x: float = 0.0,
        orbit_center_y: float = 0.0,
        orbit_rx: float = 0.0,
        orbit_ry: float = 0.0,
        orbit_theta: float = 0.0,
        orbit_tilt: float = 0.0,
        orbit_rot_speed: float = 0.0,
    ):
        self.base_x = base_x
        self.base_y = base_y
        self.color = color
        self.radius = radius
        self.phase = phase
        self.amp_x = amp_x
        self.amp_y = amp_y
        self.speed = speed
        self.sway_factor = sway_factor
        self.kind = kind

        self.rel_x = rel_x
        self.rel_y = rel_y
        self.petal_idx = petal_idx
        self.u = u

        self.orbit_center_x = orbit_center_x
        self.orbit_center_y = orbit_center_y
        self.orbit_rx = orbit_rx
        self.orbit_ry = orbit_ry
        self.orbit_theta = orbit_theta
        self.orbit_tilt = orbit_tilt
        self.orbit_rot_speed = orbit_rot_speed

    def get_pos(self, t: float, stem_sway: float, bloom: float) -> tuple[float, float]:
        ox = math.cos(t * self.speed + self.phase) * self.amp_x
        oy = math.sin(t * self.speed * 1.15 + self.phase) * self.amp_y

        sway_dx = stem_sway * self.sway_factor
        sway_dy = -abs(stem_sway * self.sway_factor) * 0.12

        if self.kind == "petal":
            # Respiración y onda entre pétalos de la flor
            petal_wave = 1.0 + bloom * (0.65 + 0.35 * self.u) * math.sin(
                t * 2.2 - self.petal_idx * 0.75 + self.u * 2.0
            )
            lift = -bloom * 7.5 * (self.u ** 1.3) * math.sin(t * 2.2 - self.petal_idx * 0.5)
            x = self.base_x + self.rel_x * petal_wave + ox + sway_dx
            y = self.base_y + self.rel_y * petal_wave + lift + oy + sway_dy
            return x, y

        if self.kind == "orbit":
            # El anillo gira sobre sí mismo y además el centro acompaña el balanceo de la flor
            theta = self.orbit_theta + t * self.orbit_rot_speed
            # Pequeña variación dinámica en el eje Y para dar efecto de rotación espacial
            dynamic_ry = self.orbit_ry * (0.86 + 0.14 * math.sin(t * 1.1 + self.orbit_tilt))

            lx = math.cos(theta) * self.orbit_rx
            ly = math.sin(theta) * dynamic_ry

            cos_t = math.cos(self.orbit_tilt)
            sin_t = math.sin(self.orbit_tilt)

            rx = lx * cos_t - ly * sin_t
            ry = lx * sin_t + ly * cos_t

            x = self.orbit_center_x + rx + ox * 0.6 + sway_dx
            y = self.orbit_center_y + ry + oy * 0.6 + sway_dy
            return x, y

        x = self.base_x + ox + sway_dx
        y = self.base_y + oy + sway_dy
        return x, y


def build_ground_particles(cx: float, ground_y: float, count: int = 2400) -> list[Particle]:
    particles = []
    for _ in range(count):
        u = random.gauss(0, 0.34)
        u = max(-1.0, min(1.0, u))
        x = cx + u * (WIDTH * 0.48)

        depth = random.random() ** 1.45
        y = ground_y - 18 + depth * 155 + random.gauss(0, 5)
        y += (1.0 - abs(u)) * 8.0 * (1.0 - depth)

        color = random.choice(GROUND_PAL)
        if random.random() < 0.08:
            color = (200, 210, 245)
        radius = random.uniform(1.0, 2.2) * (0.75 + 0.5 * depth)
        particles.append(
            Particle(
                base_x=x,
                base_y=y,
                color=color,
                radius=radius,
                phase=random.uniform(0, math.tau),
                amp_x=random.uniform(0.6, 2.0),
                amp_y=random.uniform(0.4, 1.3),
                speed=random.uniform(1.2, 2.8),
                sway_factor=0.0,
                kind="ground",
            )
        )
    return particles


def build_stem_and_leaves(cx: float, base_y: float, top_y: float) -> list[Particle]:
    particles = []
    stem_height = base_y - top_y

    stem_points = 340
    for i in range(stem_points):
        s = i / (stem_points - 1)
        y = base_y - s * stem_height
        curve_x = math.sin(s * math.pi * 1.1) * 14.0
        thickness = 11.0 * (1.0 - 0.35 * s)
        x = cx + curve_x + random.gauss(0, thickness * 0.42)

        color = random.choice(LEAF_PAL)
        particles.append(
            Particle(
                base_x=x,
                base_y=y,
                color=color,
                radius=random.uniform(1.3, 2.3),
                phase=random.uniform(0, math.tau),
                amp_x=random.uniform(0.8, 1.8),
                amp_y=random.uniform(0.8, 1.8),
                speed=random.uniform(1.8, 3.2),
                sway_factor=s,
                kind="stem",
            )
        )

    leaf_specs = [
        (0.24, -1, 135, 46, -0.42),
        (0.30, 1, 140, 48, -0.36),
        (0.46, -1, 125, 42, -0.52),
        (0.52, 1, 120, 40, -0.45),
    ]

    for h_frac, side, length, width, tilt in leaf_specs:
        attach_y = base_y - h_frac * stem_height
        attach_x = cx + math.sin(h_frac * math.pi * 1.1) * 14.0
        sway_f = h_frac + 0.08

        n_leaf_pts = 420
        for _ in range(n_leaf_pts):
            t_len = random.random() ** 0.85
            profile = math.sin(t_len * math.pi) ** 0.72
            local_x = side * t_len * length
            local_y_offset = random.uniform(-1.0, 1.0) * (width * 0.5) * profile

            cos_t = math.cos(tilt)
            sin_t = math.sin(tilt)
            rx = local_x * cos_t - local_y_offset * sin_t
            ry = local_x * sin_t + local_y_offset * cos_t

            color = (95, 175, 255) if abs(local_y_offset) < 3.0 else random.choice(LEAF_PAL)

            particles.append(
                Particle(
                    base_x=attach_x + rx,
                    base_y=attach_y + ry,
                    color=color,
                    radius=random.uniform(1.2, 2.2),
                    phase=random.uniform(0, math.tau),
                    amp_x=random.uniform(1.0, 2.2),
                    amp_y=random.uniform(1.0, 2.2),
                    speed=random.uniform(2.0, 3.6),
                    sway_factor=sway_f,
                    kind="leaf",
                )
            )

    return particles


def build_flower(cx: float, cy: float, sway_factor: float = 1.0) -> list[Particle]:
    particles = []

    layers = [
        (950, 8, 125, 82, 0.0, False),
        (850, 7, 102, 72, 0.24, False),
        (700, 6, 76, 58, -0.18, False),
        (520, 8, 46, 36, 0.10, True),
        (260, 14, 24, 18, 0.0, True),
    ]

    for count, num_petals, rx, ry, base_angle, is_core in layers:
        for _ in range(count):
            petal_idx = random.randrange(num_petals)
            petal_center_angle = base_angle + (petal_idx / num_petals) * math.tau

            u = random.random() ** 0.65
            v = random.gauss(0, 0.42)
            v = max(-1.0, min(1.0, v))

            petal_width = (math.sin(u * math.pi) ** 0.65) * (math.tau / num_petals) * 0.58
            angle = petal_center_angle + v * petal_width

            px = math.cos(angle) * rx * u
            py = math.sin(angle) * ry * u - (u ** 1.4) * (ry * 0.28)

            if is_core:
                color = random.choice(CORE_PAL)
                rad = random.uniform(1.4, 2.5)
            else:
                if u > 0.72 and random.random() < 0.35:
                    color = (125, 175, 255)
                else:
                    color = random.choice(PETAL_PAL)
                rad = random.uniform(1.3, 2.3)

            particles.append(
                Particle(
                    base_x=cx,
                    base_y=cy,
                    color=color,
                    radius=rad,
                    phase=random.uniform(0, math.tau),
                    amp_x=random.uniform(1.1, 2.4),
                    amp_y=random.uniform(1.1, 2.4),
                    speed=random.uniform(2.0, 3.8),
                    sway_factor=sway_factor,
                    kind="petal",
                    rel_x=px,
                    rel_y=py,
                    petal_idx=petal_idx,
                    u=u,
                )
            )

    return particles


def build_orbital_rings(cx: float, cy: float, sway_factor: float = 1.0) -> list[Particle]:
    particles = []

    # (radio_x, radio_y, inclinacion_rad, num_puntos, dispersion, velocidad_rotacion)
    rings = [
        (235, 235, 0.0, 340, 2.2, 0.22),
        (145, 215, 0.38, 220, 2.5, -0.35),
        (215, 130, -0.45, 200, 2.5, 0.42),
        (170, 170, 0.85, 170, 3.0, -0.28),
    ]

    for rx, ry, tilt, n_pts, spread, rot_speed in rings:
        for i in range(n_pts):
            if random.random() < 0.14:
                continue

            theta = (i / n_pts) * math.tau + random.gauss(0, 0.015)
            r_x = rx + random.gauss(0, spread)
            r_y = ry + random.gauss(0, spread)

            color = random.choice(ORBIT_PAL)
            radius = random.uniform(1.1, 2.2) if random.random() < 0.85 else random.uniform(2.3, 3.2)

            particles.append(
                Particle(
                    base_x=cx,
                    base_y=cy,
                    color=color,
                    radius=radius,
                    phase=theta * 2.0 + random.uniform(0, 1.0),
                    amp_x=random.uniform(0.7, 1.6),
                    amp_y=random.uniform(0.7, 1.6),
                    speed=random.uniform(1.6, 3.0),
                    sway_factor=sway_factor * 0.75,
                    kind="orbit",
                    orbit_center_x=cx,
                    orbit_center_y=cy,
                    orbit_rx=r_x,
                    orbit_ry=r_y,
                    orbit_theta=theta,
                    orbit_tilt=tilt,
                    orbit_rot_speed=rot_speed,
                )
            )

    return particles


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    cx = WIDTH * 0.5
    ground_y = HEIGHT * 0.76
    flower_y = HEIGHT * 0.42

    particles: list[Particle] = []
    particles.extend(build_ground_particles(cx, ground_y, count=2400))
    particles.extend(build_stem_and_leaves(cx, ground_y - 6, flower_y + 18))
    particles.extend(build_flower(cx, flower_y, sway_factor=1.0))
    particles.extend(build_orbital_rings(cx, flower_y, sway_factor=0.8))

    t = 0.0
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        t += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        stem_sway = math.sin(t * 1.35) * 14.0 + math.sin(t * 2.7) * 3.5
        # Intensidad del movimiento de apertura/onda de la flor (0.08 = sutil, 0.20 = más marcado)
        bloom = 0.11

        screen.fill((4, 5, 10))
        glow_surface.fill((0, 0, 0, 0))

        for p in particles:
            x, y = p.get_pos(t, stem_sway, bloom)
            ix, iy = int(x), int(y)
            if 0 <= ix < WIDTH and 0 <= iy < HEIGHT:
                twinkle = 0.82 + 0.18 * math.sin(t * (p.speed * 1.4) + p.phase)
                r = min(255, int(p.color[0] * twinkle))
                g = min(255, int(p.color[1] * twinkle))
                b = min(255, int(p.color[2] * twinkle))
                col = (r, g, b)

                pygame.draw.circle(screen, col, (ix, iy), max(1, int(round(p.radius))))

                if p.kind in ("petal", "orbit") and p.radius >= 1.9 and random.random() < 0.35:
                    pygame.draw.circle(
                        glow_surface,
                        (r // 3, g // 3, b // 2, 35),
                        (ix, iy),
                        int(round(p.radius * 2.4)),
                    )

        screen.blit(glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

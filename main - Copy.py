import pygame
import sys
import random
import heapq
import os
import tkinter as tk
from tkinter import filedialog

pygame.init()
def pilih_peta():
    root = tk.Tk()
    root.withdraw()  # Supaya nggak muncul jendela Tkinter utama
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        return load_image(file_path)
    return None

# Warna tambahan
BIRU = (0, 0, 255)
KUNING = (255, 255, 0)
MERAH = (255, 0, 0)
PUTIH = (255, 255, 255)

# Konfigurasi window
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 700
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Simulasi Smart Courier")

# Load gambar
def load_image(path):
    if not os.path.exists(path):
        print(f"❌ File tidak ditemukan: {path}")
        pygame.quit()
        sys.exit()
    return pygame.image.load(path)

peta = pilih_peta()
if peta is None:
    print("❌ Tidak ada peta dipilih. Program dihentikan.")
    pygame.quit()
    sys.exit()

mobil_ori = pygame.transform.scale(load_image("mobil.png"), (50, 30))
bendera_kuning = pygame.transform.scale(load_image("source_flag.png"), (30, 30))
bendera_merah = pygame.transform.scale(load_image("destination_flag.png"), (30, 30))

# Inisialisasi posisi mobil
mobil_rect = mobil_ori.get_rect()
mobil_rect.topleft = (100, 100)
mobil_arah = "kanan"

# Kecepatan mobil
kecepatan = 5
mengantar = False

# Anti-nyangkut
last_positions = []
nyangkut_counter = 0
threshold_stuck = 60
threshold_movement = 3

# Cek apakah berada di jalan
def is_on_road(x, y):
    if 0 <= x + 25 < peta.get_width() and 0 <= y + 15 < peta.get_height():
        color = peta.get_at((x + 25, y + 15))
        return 90 <= color.r <= 150 and 90 <= color.g <= 150 and 90 <= color.b <= 150
    return False

# Dapatkan posisi acak di jalan
def acak_posisi():
    while True:
        x = random.randint(0, peta.get_width() - 50)
        y = random.randint(0, peta.get_height() - 50)
        if is_on_road(x, y):
            return x, y

source_pos = acak_posisi()
dest_pos = acak_posisi()

# Rotasi mobil
def rotasi_mobil(arah):
    if arah == "kanan":
        return mobil_ori
    elif arah == "kiri":
        return pygame.transform.flip(mobil_ori, True, False)
    elif arah == "atas":
        return pygame.transform.rotate(mobil_ori, 90)
    elif arah == "bawah":
        return pygame.transform.rotate(mobil_ori, -90)

def is_facing(mobil_rect, arah, target_pos):
    dx = target_pos[0] - mobil_rect.centerx
    dy = target_pos[1] - mobil_rect.centery
    if arah == "kanan" and dx > 0:
        return True
    elif arah == "kiri" and dx < 0:
        return True
    elif arah == "atas" and dy < 0:
        return True
    elif arah == "bawah" and dy > 0:
        return True
    return False

# A* Pathfinding
def astar(start, goal):
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        _, current = heapq.heappop(open_set)

        if heuristic(current, goal) < 10:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in [(kecepatan, 0), (-kecepatan, 0), (0, kecepatan), (0, -kecepatan)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if not is_on_road(*neighbor):
                continue
            tentative_g = g_score[current] + heuristic(current, neighbor)
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []

# Gerak otomatis
path = []
def move_along_path(mobil_rect, path, arah):
    if not path:
        return arah
    target = path[0]
    dx = target[0] - mobil_rect.x
    dy = target[1] - mobil_rect.y

    if abs(dx) > abs(dy):
        mobil_rect.x += kecepatan if dx > 0 else -kecepatan
        arah = "kanan" if dx > 0 else "kiri"
    else:
        mobil_rect.y += kecepatan if dy > 0 else -kecepatan
        arah = "bawah" if dy > 0 else "atas"

    if abs(dx) < kecepatan and abs(dy) < kecepatan:
        path.pop(0)
    return arah

# Loop utama
clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    window.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                mobil_rect.topleft = acak_posisi()
            elif event.key == pygame.K_l:
                new_peta = pilih_peta()
                if new_peta:
                    peta = new_peta
                    source_pos = acak_posisi()
                    dest_pos = acak_posisi()
                    mobil_rect.topleft = acak_posisi()
                    path = []
                    print("🗺️ Peta baru berhasil dimuat!")

            elif event.key == pygame.K_t:
                source_pos = acak_posisi()
                dest_pos = acak_posisi()
                mengantar = False
                path = []

    old_position = mobil_rect.topleft
    keys = pygame.key.get_pressed()

    if not mengantar:
        if keys[pygame.K_LEFT]:
            mobil_rect.x -= kecepatan
            mobil_arah = "kiri"
        elif keys[pygame.K_RIGHT]:
            mobil_rect.x += kecepatan
            mobil_arah = "kanan"
        elif keys[pygame.K_UP]:
            mobil_rect.y -= kecepatan
            mobil_arah = "atas"
        elif keys[pygame.K_DOWN]:
            mobil_rect.y += kecepatan
            mobil_arah = "bawah"
    else:
        if not path:
            path = astar(mobil_rect.topleft, dest_pos)
        else:
            mobil_arah = move_along_path(mobil_rect, path, mobil_arah)

        # Deteksi nyangkut
        last_positions.append(mobil_rect.topleft)
        if len(last_positions) > threshold_stuck:
            last_positions.pop(0)
            moved = any(
                abs(last_positions[-1][0] - pos[0]) > threshold_movement or
                abs(last_positions[-1][1] - pos[1]) > threshold_movement
                for pos in last_positions
            )
            if not moved:
                print("⚠️ Mobil nyangkut! Reset ke source.")
                mobil_rect.topleft = source_pos
                path = astar(mobil_rect.topleft, dest_pos)
                last_positions.clear()

    # Jika keluar dari jalan, kembalikan posisi
    if not is_on_road(mobil_rect.x, mobil_rect.y):
        mobil_rect.topleft = old_position

    # Ambil paket
    if not mengantar and mobil_rect.colliderect(pygame.Rect(source_pos, (30, 30))) and is_facing(mobil_rect, mobil_arah, source_pos):
        mengantar = True
        path = []
        print("📦 Paket diambil!")

    # Antar paket
    if mengantar and mobil_rect.colliderect(pygame.Rect(dest_pos, (30, 30))):
        mengantar = False
        path = []
        print("✅ Paket diantar!")

    # Kamera mengikuti mobil
    camera_x = max(0, min(mobil_rect.centerx - WINDOW_WIDTH // 2, peta.get_width() - WINDOW_WIDTH))
    camera_y = max(0, min(mobil_rect.centery - WINDOW_HEIGHT // 2, peta.get_height() - WINDOW_HEIGHT))

    window.blit(peta, (-camera_x, -camera_y))
    window.blit(bendera_kuning, (source_pos[0] - camera_x, source_pos[1] - camera_y))
    window.blit(bendera_merah, (dest_pos[0] - camera_x, dest_pos[1] - camera_y))
    window.blit(rotasi_mobil(mobil_arah), (mobil_rect.x - camera_x, mobil_rect.y - camera_y))

    # ========== MINI MAP ==========
    MINI_MAP_WIDTH, MINI_MAP_HEIGHT = 200, 140
    MINI_SCALE_X = MINI_MAP_WIDTH / peta.get_width()
    MINI_SCALE_Y = MINI_MAP_HEIGHT / peta.get_height()
    MINI_POS_X, MINI_POS_Y = WINDOW_WIDTH - MINI_MAP_WIDTH - 20, WINDOW_HEIGHT - MINI_MAP_HEIGHT - 20

    # Gambar latar mini map (dari peta asli, diperkecil)
    mini_peta = pygame.transform.smoothscale(peta, (MINI_MAP_WIDTH, MINI_MAP_HEIGHT))
    
    # Gambar border minimap terlebih dahulu
    pygame.draw.rect(window, PUTIH, (MINI_POS_X - 2, MINI_POS_Y - 2, MINI_MAP_WIDTH + 4, MINI_MAP_HEIGHT + 4), 2)
    
    # Gambar minimap
    window.blit(mini_peta, (MINI_POS_X, MINI_POS_Y))

    # Fungsi untuk menggambar titik di minimap
    def draw_mini_dot(pos, color, size=4):
        mini_x = int(pos[0] * MINI_SCALE_X) + MINI_POS_X
        mini_y = int(pos[1] * MINI_SCALE_Y) + MINI_POS_Y
        pygame.draw.circle(window, color, (mini_x, mini_y), size)

    # Gambar titik-titik penting di minimap
    draw_mini_dot((mobil_rect.x + 25, mobil_rect.y + 15), BIRU)  # Posisi kurir (pusat mobil)
    draw_mini_dot((source_pos[0] + 15, source_pos[1] + 15), KUNING)  # Posisi source (pusat bendera)
    draw_mini_dot((dest_pos[0] + 15, dest_pos[1] + 15), MERAH)  # Posisi destination (pusat bendera)

    pygame.display.flip()

pygame.quit()
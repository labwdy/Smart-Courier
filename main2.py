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
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if file_path:
        return load_image(file_path)
    return None

BIRU = (0, 0, 255)
KUNING = (255, 255, 0)
MERAH = (255, 0, 0)
PUTIH = (255, 255, 255)

WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 700
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Simulasi Smart Courier")

font_info = pygame.font.SysFont("arial", 22)
font_status = pygame.font.SysFont("arial", 26)

status_pesan = "Tekan S untuk memulai"
tampilkan_petunjuk_awal = True
petunjuk_awal = [
    "Tekan S untuk memulai",
    "Tekan T untuk mengacak ulang source dan destination",
    "Tekan R untuk reset posisi mobil",
    "Tekan L untuk memuat peta baru"
]

def tampilkan_pesan_layar(teks, warna=(255, 255, 255)):
    teks_render = font_status.render(teks, True, warna)
    window.blit(teks_render, (WINDOW_WIDTH // 2 - teks_render.get_width() // 2, 10))

def tampilkan_petunjuk():
    if tampilkan_petunjuk_awal:
        for i, teks in enumerate(petunjuk_awal):
            teks_render = font_info.render(teks, True, PUTIH)
            window.blit(teks_render, (20, 50 + i * 30))

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
mobil_rect = mobil_ori.get_rect()

kecepatan = 5
mobil_arah = "kanan"
program_dimulai = False
menuju_source = False
mengantar = False

last_positions = []
threshold_stuck = 60
threshold_movement = 3

def is_on_road(x, y):
    if 0 <= x + 25 < peta.get_width() and 0 <= y + 15 < peta.get_height():
        color = peta.get_at((x + 25, y + 15))
        return 90 <= color.r <= 150 and 90 <= color.g <= 150 and 90 <= color.b <= 150
    return False

def acak_posisi():
    while True:
        x = random.randint(0, peta.get_width() - mobil_rect.width)
        y = random.randint(0, peta.get_height() - mobil_rect.height)
        if is_on_road(x, y):
            return x, y

def acak_posisi_dekat(center, jarak_maks=150):
    for _ in range(1000):
        dx = random.randint(-jarak_maks, jarak_maks)
        dy = random.randint(-jarak_maks, jarak_maks)
        x = center[0] + dx
        y = center[1] + dy
        if 0 <= x < peta.get_width() - mobil_rect.width and 0 <= y < peta.get_height() - mobil_rect.height:
            if is_on_road(x, y):
                return x, y
    return acak_posisi()

source_pos = acak_posisi()
mobil_rect.topleft = acak_posisi_dekat(source_pos)
dest_pos = acak_posisi()

path = []

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
    return (arah == "kanan" and dx > 0) or \
           (arah == "kiri" and dx < 0) or \
           (arah == "atas" and dy < 0) or \
           (arah == "bawah" and dy > 0)

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

def move_along_path(mobil_rect, path, arah):
    if not path:
        return arah
    target = path[0]
    dx = target[0] - mobil_rect.x
    dy = target[1] - mobil_rect.y

    if abs(dx) > 0:
        mobil_rect.x += kecepatan if dx > 0 else -kecepatan
        arah = "kanan" if dx > 0 else "kiri"
    elif abs(dy) > 0:
        mobil_rect.y += kecepatan if dy > 0 else -kecepatan
        arah = "bawah" if dy > 0 else "atas"
        
    if abs(dx) <= kecepatan and abs(dy) <= kecepatan:
        mobil_rect.topleft = target
        path.pop(0)
    return arah

clock = pygame.time.Clock()
running = True
while running:
    clock.tick(60)
    window.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                program_dimulai = True
                menuju_source = True
                path = astar(mobil_rect.topleft, source_pos)
                status_pesan = "Menuju ke sumber sortir (bendera kuning)..."
                tampilkan_petunjuk_awal = False
            elif event.key == pygame.K_r:
                mobil_rect.topleft = acak_posisi_dekat(source_pos)
            elif event.key == pygame.K_l:
                new_peta = pilih_peta()
                if new_peta:
                    peta = new_peta
                    source_pos = acak_posisi()
                    mobil_rect.topleft = acak_posisi_dekat(source_pos)
                    dest_pos = acak_posisi()
                    path = []
                    status_pesan = "Peta baru dimuat"
            elif event.key == pygame.K_t:
                source_pos = acak_posisi()
                mobil_rect.topleft = acak_posisi_dekat(source_pos)
                dest_pos = acak_posisi()
                path = []
                program_dimulai = True
                menuju_source = True
                mengantar = False
                status_pesan = "Bendera diacak. Menuju ke sumber sortir."

    old_position = mobil_rect.topleft

    if program_dimulai:
        if menuju_source and not path:
            path = astar(mobil_rect.topleft, source_pos)
        elif menuju_source:
            mobil_arah = move_along_path(mobil_rect, path, mobil_arah)
            if mobil_rect.colliderect(pygame.Rect(source_pos, (30, 30))) and is_facing(mobil_rect, mobil_arah, source_pos):
                menuju_source = False
                mengantar = True
                path = astar(mobil_rect.topleft, dest_pos)
                status_pesan = "Paket diambil! Menuju ke tujuan."
        elif mengantar and not path:
            path = astar(mobil_rect.topleft, dest_pos)
        elif mengantar:
            mobil_arah = move_along_path(mobil_rect, path, mobil_arah)
            if mobil_rect.colliderect(pygame.Rect(dest_pos, (30, 30))):
                mengantar = False
                program_dimulai = False
                path = []
                status_pesan = "Paket berhasil diantar!"

    if not is_on_road(mobil_rect.x, mobil_rect.y):
        mobil_rect.topleft = old_position

    camera_x = max(0, min(mobil_rect.centerx - WINDOW_WIDTH // 2, peta.get_width() - WINDOW_WIDTH))
    camera_y = max(0, min(mobil_rect.centery - WINDOW_HEIGHT // 2, peta.get_height() - WINDOW_HEIGHT))

    window.blit(peta, (-camera_x, -camera_y))
    window.blit(bendera_kuning, (source_pos[0] - camera_x, source_pos[1] - camera_y))
    window.blit(bendera_merah, (dest_pos[0] - camera_x, dest_pos[1] - camera_y))
    window.blit(rotasi_mobil(mobil_arah), (mobil_rect.x - camera_x, mobil_rect.y - camera_y))

    MINI_MAP_WIDTH, MINI_MAP_HEIGHT = 200, 140
    MINI_SCALE_X = MINI_MAP_WIDTH / peta.get_width()
    MINI_SCALE_Y = MINI_MAP_HEIGHT / peta.get_height()
    MINI_POS_X, MINI_POS_Y = WINDOW_WIDTH - MINI_MAP_WIDTH - 20, WINDOW_HEIGHT - MINI_MAP_HEIGHT - 20

    mini_peta = pygame.transform.smoothscale(peta, (MINI_MAP_WIDTH, MINI_MAP_HEIGHT))
    pygame.draw.rect(window, PUTIH, (MINI_POS_X - 2, MINI_POS_Y - 2, MINI_MAP_WIDTH + 4, MINI_MAP_HEIGHT + 4), 2)
    window.blit(mini_peta, (MINI_POS_X, MINI_POS_Y))

    def draw_mini_dot(pos, color, size=4):
        mini_x = int(pos[0] * MINI_SCALE_X) + MINI_POS_X
        mini_y = int(pos[1] * MINI_SCALE_Y) + MINI_POS_Y
        pygame.draw.circle(window, color, (mini_x, mini_y), size)

    draw_mini_dot((mobil_rect.x + 25, mobil_rect.y + 15), BIRU)
    draw_mini_dot((source_pos[0] + 15, source_pos[1] + 15), KUNING)
    draw_mini_dot((dest_pos[0] + 15, dest_pos[1] + 15), MERAH)

    if path:
        path_screen = [(x - camera_x + 25, y - camera_y + 15) for (x, y) in path]
        if len(path_screen) > 1:
            pygame.draw.lines(window, (0, 255, 255), False, path_screen, 2)

    tampilkan_petunjuk()
    tampilkan_pesan_layar(status_pesan)
    pygame.display.flip()

pygame.quit()

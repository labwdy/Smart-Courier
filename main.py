import pygame
import sys

# Inisialisasi pygame
pygame.init()

# Ukuran window sesuai ukuran peta
WIDTH, HEIGHT = 768, 768
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulasi Mobil Kurir")

# Load gambar
peta = pygame.image.load("peta.png").convert()
mobil = pygame.image.load("mobil.png").convert_alpha()

# Ubah ukuran mobil jika terlalu besar
mobil = pygame.transform.scale(mobil, (50, 30))

# Posisi awal mobil
x, y = 100, 100
kecepatan = 5

# Arah awal mobil
arah = 0  # 0 derajat (kanan)

# Loop utama
running = True
while running:
    screen.blit(peta, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Kontrol arah
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        x -= kecepatan
        arah = 180
    if keys[pygame.K_RIGHT]:
        x += kecepatan
        arah = 0
    if keys[pygame.K_UP]:
        y -= kecepatan
        arah = 90
    if keys[pygame.K_DOWN]:
        y += kecepatan
        arah = -90  # -90 = 270 derajat (bawah)

    # Rotasi mobil sesuai arah
    mobil_rotasi = pygame.transform.rotate(mobil, arah)

    # Perbaikan posisi agar rotasi tidak geser
    rect = mobil_rotasi.get_rect(center=(x + 25, y + 15))
    screen.blit(mobil_rotasi, rect.topleft)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()

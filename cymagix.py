import cupy as cp
import numpy as np
import pygame
from scipy.ndimage import gaussian_filter
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# Pygame initialization
pygame.init()
window_size = (1600, 900)  # Initial window size
screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)  # Allow window to be resizable
pygame.display.set_caption("3D Cymatics Simulator")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (200, 200, 200)
RED = (255, 0, 0)

# Font
font = pygame.font.SysFont(None, 24)

# Slider values
hz_value = 0
khz_value = 0
mhz_value = 0
ghz_value = 0

# View angles for 3D plot
elevation = 30
azimuth = 45
dragging = False
last_mouse_pos = (0, 0)

# Colormaps
colormaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']
current_colormap_index = 0

def generate_sine_wave(frequency, duration, sampling_rate=44100, amplitude=200.0):  # Doubled amplitude
    t = cp.linspace(0, duration, int(sampling_rate * duration), endpoint=False)
    wave = amplitude * cp.sin(2 * cp.pi * frequency * t)
    return wave

def visualize_cymatics_3d(frequency, time_step, sampling_rate=44100, grid_size=(100, 100), amplitude=200.0):  # Adjusted amplitude
    wave = generate_sine_wave(frequency, 1, sampling_rate, amplitude)
    k = 2 * cp.pi * frequency / sampling_rate
    x = cp.linspace(-1, 1, grid_size[0])
    y = cp.linspace(-1, 1, grid_size[1])
    X, Y = cp.meshgrid(x, y)
    distance = cp.sqrt(X**2 + Y**2)
    
    grid = wave[time_step] * cp.sin(k * distance)
    grid = cp.abs(grid)
    grid = cp.asnumpy(grid)
    grid = gaussian_filter(grid, sigma=1)
    
    X = cp.asnumpy(X)
    Y = cp.asnumpy(Y)
    
    return X, Y, grid

def draw_3d_cymatics_pattern(X, Y, Z, elev, azim, colormap):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, cmap=colormap, edgecolor='none')
    ax.set_zlim(-300, 300)  # Adjust z-axis limit to make the pattern more pronounced
    ax.view_init(elev=elev, azim=azim)  # Set view angle
    canvas = FigureCanvas(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()

    plt.close(fig)  # Close the figure after rendering to free up resources

    return pygame.image.frombuffer(raw_data, size, 'RGBA')

def draw_top_down_cymatics_pattern(X, Y, Z, colormap):
    fig, ax = plt.subplots()
    c = ax.pcolormesh(X, Y, Z, cmap=colormap, shading='auto')  # Use selected colormap
    fig.colorbar(c, ax=ax)
    canvas = FigureCanvas(fig)
    canvas.draw()
    renderer = canvas.get_renderer()
    raw_data = renderer.buffer_rgba()
    size = canvas.get_width_height()

    plt.close(fig)  # Close the figure after rendering to free up resources

    return pygame.image.frombuffer(raw_data, size, 'RGBA')

def draw_slider(screen, rect, value, max_value, label):
    pygame.draw.rect(screen, GREY, rect)
    knob_x = rect.x + (value / max_value) * (rect.width - 20)  # 20 is the knob width
    pygame.draw.rect(screen, BLACK, (knob_x, rect.y - 10, 20, 40))  # Adjust knob position
    label_surface = font.render(label + f": {value:.2f}", True, BLACK)
    screen.blit(label_surface, (rect.x, rect.y - 30))

def draw_reset_button(screen, rect):
    pygame.draw.rect(screen, RED, rect)
    label_surface = font.render("Reset", True, WHITE)
    screen.blit(label_surface, (rect.x + 20, rect.y + 10))

def draw_colormap_button(screen, rect, label):
    pygame.draw.rect(screen, GREY, rect)
    label_surface = font.render(label, True, BLACK)
    screen.blit(label_surface, (rect.x + 10, rect.y + 10))

def reset_simulation():
    global hz_value, khz_value, mhz_value, ghz_value
    hz_value = 0
    khz_value = 0
    mhz_value = 0
    ghz_value = 0

def save_cymatics_image(X, Y, Z, filename, colormap):
    fig, ax = plt.subplots()
    c = ax.pcolormesh(X, Y, Z, cmap=colormap, shading='auto')  # Use selected colormap
    fig.colorbar(c, ax=ax)
    fig.savefig(filename)
    plt.close(fig)

def main():
    global hz_value, khz_value, mhz_value, ghz_value, window_size, screen, elevation, azimuth, dragging, last_mouse_pos, current_colormap_index

    running = True
    clock = pygame.time.Clock()
    time_step = 0
    mouse_dragging = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                window_size = event.size
                screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    hz_slider_rect = pygame.Rect(100, window_size[1] - 100, 200, 30)
                    khz_slider_rect = pygame.Rect(400, window_size[1] - 100, 200, 30)
                    mhz_slider_rect = pygame.Rect(700, window_size[1] - 100, 200, 30)
                    ghz_slider_rect = pygame.Rect(1000, window_size[1] - 100, 200, 30)
                    reset_button_rect = pygame.Rect(window_size[0] - 200, window_size[1] - 100, 100, 40)
                    colormap_button_rect = pygame.Rect(window_size[0] - 400, window_size[1] - 100, 150, 40)
                    if hz_slider_rect.collidepoint(event.pos):
                        dragging = 'hz'
                    elif khz_slider_rect.collidepoint(event.pos):
                        dragging = 'khz'
                    elif mhz_slider_rect.collidepoint(event.pos):
                        dragging = 'mhz'
                    elif ghz_slider_rect.collidepoint(event.pos):
                        dragging = 'ghz'
                    elif reset_button_rect.collidepoint(event.pos):
                        reset_simulation()
                    elif colormap_button_rect.collidepoint(event.pos):
                        current_colormap_index = (current_colormap_index + 1) % len(colormaps)
                    else:
                        mouse_dragging = True
                        last_mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = None
                mouse_dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging == 'hz':
                    hz_value = (event.pos[0] - hz_slider_rect.x) / hz_slider_rect.width * 999
                elif dragging == 'khz':
                    khz_value = (event.pos[0] - khz_slider_rect.x) / khz_slider_rect.width * 999
                elif dragging == 'mhz':
                    mhz_value = (event.pos[0] - mhz_slider_rect.x) / mhz_slider_rect.width * 1
                elif dragging == 'ghz':
                    ghz_value = (event.pos[0] - ghz_slider_rect.x) / ghz_slider_rect.width * 1
                elif mouse_dragging:
                    dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
                    elevation += dy * 0.2
                    azimuth += dx * 0.2
                    last_mouse_pos = event.pos

        screen.fill(WHITE)

        total_frequency = hz_value + khz_value * 1000 + mhz_value * 1000000 + ghz_value * 1000000000
        X, Y, Z = visualize_cymatics_3d(total_frequency, time_step % 100)

        current_colormap = colormaps[current_colormap_index]
        cymatics_surface_3d = draw_3d_cymatics_pattern(X, Y, Z, elevation, azimuth, current_colormap)
        cymatics_surface_top = draw_top_down_cymatics_pattern(X, Y, Z, current_colormap)

        screen.blit(cymatics_surface_3d, (0, 0))
        screen.blit(cymatics_surface_top, (window_size[0] // 2, 0))

        hz_slider_rect = pygame.Rect(100, window_size[1] - 100, 200, 30)
        khz_slider_rect = pygame.Rect(400, window_size[1] - 100, 200, 30)
        mhz_slider_rect = pygame.Rect(700, window_size[1] - 100, 200, 30)
        ghz_slider_rect = pygame.Rect(1000, window_size[1] - 100, 200, 30)
        reset_button_rect = pygame.Rect(window_size[0] - 200, window_size[1] - 100, 100, 40)
        colormap_button_rect = pygame.Rect(window_size[0] - 400, window_size[1] - 100, 150, 40)

        draw_slider(screen, hz_slider_rect, hz_value, 999, "Hz")
        draw_slider(screen, khz_slider_rect, khz_value, 999, "kHz")
        draw_slider(screen, mhz_slider_rect, mhz_value, 1, "MHz")
        draw_slider(screen, ghz_slider_rect, ghz_value, 1, "GHz")

        draw_reset_button(screen, reset_button_rect)
        draw_colormap_button(screen, colormap_button_rect, "Change Colormap")

        # Display total frequency
        total_freq_surface = font.render(f"Total Frequency: {total_frequency:.2f} Hz", True, BLACK)
        screen.blit(total_freq_surface, (window_size[0] // 2 - total_freq_surface.get_width() // 2, window_size[1] - 150))

        # Save image when the 's' key is pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            save_cymatics_image(X, Y, Z, 'cymatics_pattern.png', current_colormap)

        pygame.display.flip()
        clock.tick(30)  # Increase frame rate to 30 FPS for smoother animation
        time_step += 1

    pygame.quit()

if __name__ == "__main__":
    main()

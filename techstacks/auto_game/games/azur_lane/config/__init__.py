from matplotlib import pyplot as plt

DIR_BASE = "D:/Projects/Python/JustCode/techstacks/auto_game/games/azur_lane"
CONFIG_SCENE = "D:/Projects/Python/JustCode/techstacks/auto_game/games/azur_lane/config/scene.yaml"


def close_figure(event):
    if event.key == 'escape':
        plt.close(event.canvas.figure)


def s(x):
    plt.imshow(x)
    plt.show()
    plt.gcf().canvas.mpl_connect('key_press_event', close_figure)

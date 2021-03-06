import matplotlib
from matplotlib.axes import Axes
from matplotlib import pyplot as plt, rc, font_manager
from matplotlib.figure import Figure
from typing import Dict, Tuple
from pathlib import Path
import logging

rc('font', family='NanumGothic')
mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
matplotlib.use('Agg')


class ImageGenerator:
    def __init__(self, name, transparent: bool = False, background: str = 'FFFFFF', log_scale: bool = False):
        self.transparent = transparent
        self.background = '#' + background
        self.scale = 'log' if log_scale else 'linear'
        self.name = name

    def generate_and_save_image(self, data: Dict[str, Dict[float, float]], website: str, output: Path, latency_until: float = 100):
        figure = self.generate_image(data, website, latency_until=latency_until)
        self.save_image(figure, output)

    def generate_image(self, data: Dict[str, Dict[float, float]], website: str, latency_until: float = 100) -> Figure:
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(1, 1, 1)  # type: Axes
        for label, values in data.items():
            filtered_values = {p: v for p, v in values.items() if p <= latency_until}
            x, y = zip(*sorted(filtered_values.items()))
            y_ms = [v * 1000 for v in y]
            ax.plot(x, y_ms, label=label)
        if self.scale == 'linear':
            ax.set_ylim(bottom=max(ax.get_ylim()[0], 0))
        ax.legend()
        ax.set(title='Latency graph for %s' % self.name,
               xlabel='percentile',
               ylabel='latency [ms]' if self.scale == 'linear' else 'latency [ms] [log scale]',
               yscale=self.scale,
               facecolor=self.background)
        return fig

    def save_image(self, figure: Figure, output: Path):
        if self.transparent:
            figure.savefig(str(output), transparent=self.transparent)
        else:
            figure.savefig(str(output), facecolor=self.background)

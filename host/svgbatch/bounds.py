
class Bounds(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None

    @property
    def width(self):
        if self.xmin is not None:
            return self.xmax - self.xmin

    @property
    def height(self):
        if self.xmin is not None:
            return self.ymax - self.ymin

    def add_point(self, x, y):
        if self.xmin is None:
            self.xmin = self.xmax = x
            self.ymin = self.ymax = y
        else:
            self.xmin = min(self.xmin, x)
            self.xmax = max(self.xmax, x)
            self.ymin = min(self.ymin, y)
            self.ymax = max(self.ymax, y)

    def add_bounds(self, other):
        if other.xmin is None:
            return
        elif self.xmin is None:
            self.xmin = other.xmin
            self.xmax = other.xmax
            self.ymin = other.ymin
            self.ymax = other.ymax
        else:
            self.xmin = min(self.xmin, other.xmin)
            self.xmax = max(self.xmax, other.xmax)
            self.ymin = min(self.ymin, other.ymin)
            self.ymax = max(self.ymax, other.ymax)

    def get_center(self):
        if self.xmin:
            return (
                (self.xmin + self.xmax) / 2,
                (self.ymin + self.ymax) / 2,
            )

    def offset(self, x, y):
        if self.xmin is not None:
            self.xmin += x
            self.xmax += x
            self.ymin += y
            self.ymax += y

    def __str__(self):
        if self.xmin is None:
            return '<Bounds null>'
        return '<Bounds (%.2f, %.2f) (%.2f, %.2f)>' % (
            self.xmin, self.xmax,
            self.ymin, self.ymax)
        

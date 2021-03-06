#
# To run this script, type 'python raytrace.py'
#
# Open source Ray Tracer: https://rheiland.github.io/raytrace/
#
#
from math import sqrt, pow, pi
# 3rd party module, not part of the Python standard library (try: "easy_install pil")
from PIL import Image
import time


# Perhaps this is not the best named class; it really serves as just a 3-tuple most of the time. A mathematical
# vector would have a magnitude and direction. These are implicit by specifying a (x,y,z) 3-tuple (assumes relative
# to the origin (0,0,0).
class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, b):  # vector dot product
        return self.x*b.x + self.y*b.y + self.z*b.z

    def cross(self, b):  # vector cross product
        return (self.y*b.z-self.z*b.y, self.z*b.x-self.x*b.z, self.x*b.y-self.y*b.x)

    def magnitude(self):  # vector magnitude
        return sqrt(self.x**2+self.y**2+self.z**2)

    def normal(self):  # compute a normalized (unit length) vector
        mag = self.magnitude()
        return Vector(self.x/mag, self.y/mag, self.z/mag)

    def toScaled(self, scale: float):  # vector scaled
        return Vector(self.x * scale, self.y * scale, self.z * scale)

    def simpleMultiply(self, other):
        return Vector(self.x * other.x, self.y * other.y, self.z * other.z)

        # Provide "overridden methods via the "__operation__" notation; allows you to do, for example, a+b, a-b, a*b
    def __add__(self, b):  # add another vector (b) to a given vector (self)
        return Vector(self.x + b.x, self.y+b.y, self.z+b.z)

    def __sub__(self, b):  # subtract another vector (b) from a given vector (self)
        return Vector(self.x-b.x, self.y-b.y, self.z-b.z)

    def __mul__(self, b):  # scalar multiplication of a given vector
        assert type(b) == float or type(b) == int
        return Vector(self.x*b, self.y*b, self.z*b)


class Sphere(object):
    def __init__(self, center, radius, color):
        self.c = center
        self.r = radius
        self.col = color

    def intersection(self, l):
        q = l.d.dot(l.o - self.c)**2 - \
            (l.o - self.c).dot(l.o - self.c) + self.r**2
        if q < 0:
            return Intersection(Vector(0, 0, 0), -1, Vector(0, 0, 0), self)
        else:
            d = -l.d.dot(l.o - self.c)
            d1 = d - sqrt(q)
            d2 = d + sqrt(q)
            if 0 < d1 and (d1 < d2 or d2 < 0):
                return Intersection(l.o+l.d*d1, d1, self.normal(l.o+l.d*d1), self)
            elif 0 < d2 and (d2 < d1 or d1 < 0):
                return Intersection(l.o+l.d*d2, d2, self.normal(l.o+l.d*d2), self)
            else:
                return Intersection(Vector(0, 0, 0), -1, Vector(0, 0, 0), self)

    def normal(self, b):
        return (b - self.c).normal()


class Plane(object):
    def __init__(self, point, normal, color):
        self.n = normal
        self.p = point
        self.col = color

    def intersection(self, l):
        d = l.d.dot(self.n)
        if d == 0:
            return Intersection(Vector(0, 0, 0), -1, Vector(0, 0, 0), self)
        else:
            d = (self.p - l.o).dot(self.n) / d
            return Intersection(l.o+l.d*d, d, self.n, self)


class Ray(object):
    def __init__(self, origin, direction):
        self.o = origin
        self.d = direction


class Intersection(object):
    def __init__(self, point, distance, normal, obj):
        self.p = point
        self.d = distance
        self.n = normal
        self.obj = obj


class DirectionalLight():
    def __init__(self, color: Vector, strength: float, direction: Vector):
        Light.__init__(self, color, strength)
        self.direction = direction


class Light:
    def __init__(self, color: Vector, strength: float):
        self.color = color
        self.strength = strength


class Point3D:
    def __init__(self, x: float, y: float, z: float):
        self.vector = Vector(x, y, z)

    def fromVector(vector: Vector):
        return Point3D(vector.x, vector.y, vector.z)

    def distance(self, other):
        vectorDifference = self.minus(other)
        return vectorDifference.length()

    def minus(self, other):
        return self.vector.minus(other.vector)


def testRay(ray, objects, ignore=None):
    intersect = Intersection(Vector(0, 0, 0), -1, Vector(0, 0, 0), None)

    for obj in objects:
        if obj is not ignore:
            currentIntersect = obj.intersection(ray)
            if currentIntersect.d > 0 and intersect.d < 0:
                intersect = currentIntersect
            elif 0 < currentIntersect.d < intersect.d:
                intersect = currentIntersect
    return intersect


def trace(ray, objects, light, maxRecur):
    if maxRecur < 0:
        return (0, 0, 0)

    # gets the intersection of objects at that point
    intersect = testRay(ray, objects)
    # print("Intersect color: ", intersect.obj.col.x)
    # print("Intersect color: ", intersect.obj.col.y)
    # print("Intersect color: ", intersect.obj.col.z)

    # set up diffuse and ambient on range [0,1]
    ambient = Vector(.1, .1, .1)  # ambient light is .1
    diffuse = Vector(0, 0, 0)

    lightDiffuse = Vector(0, 0, 0)
    toLight = light.direction.toScaled(-1)
    product = toLight.dot(intersect.n)
    if product < 0:
        product = 0
    lightDiffuse = (light.color.toScaled(product))
    lightDiffuse = (lightDiffuse.toScaled(1/255))
    diffuse = diffuse.__add__(lightDiffuse)

    print("Diffuse x:", diffuse.x)
    print("Diffuse y:", diffuse.y)
    print("Diffuse z:", diffuse.z)

    color = ambient.__add__(diffuse)
    # print("Ambient and diffuse x: ", color.x)
    # print("Ambient and diffuse y: ", color.y)
    # print("Ambient and diffuse z: ", color.z)

    # if it is the ground shadow
    if intersect.d == -1:
        col = Vector(.1, .1, .1)

    # takes care of the shadows (but not ground shadow)
    elif intersect.n.dot(light.direction - intersect.p) < 0:
        col = intersect.obj.col.simpleMultiply(color)
        # print("Multiply intersect object color and color x: ", color.x)
        # print("Multiply intersect object color and color y: ", color.y)
        # print("Multiply intersect object color and color z: ", color.z)

    else:
        lightRay = Ray(intersect.p, (light.direction-intersect.p).normal())
        if testRay(lightRay, objects, intersect.obj).d == -1:
            lightIntensity = 1000.0 / \
                (4*pi*(light.direction-intersect.p).magnitude()**2)
            col = intersect.obj.col * (max(intersect.n.normal().dot(
                (light.direction - intersect.p).normal()*lightIntensity), ambient.x))
            # print("Intersect col times the max of something and ambiencex: ", col.x)
            # print("Intersect col times the max of something and ambiencey: ", col.y)
            # print("Intersect col times the max of something and ambiencez: ", col.z)
        else:
            col = intersect.obj.col.simpleMultiply(color)
    return col


def gammaCorrection(color, factor):
    # print(int(pow(color.x/255.0, factor)*255),
    #       int(pow(color.y/255.0, factor)*255),
    #       int(pow(color.z/255.0, factor)*255))

    return (int(pow(color.x/255.0, factor)*255),
            int(pow(color.y/255.0, factor)*255),
            int(pow(color.z/255.0, factor)*255))


# AMBIENT = 0.05
GAMMA_CORRECTION = 1/2.2

objs = []   # create an empty Python "list"
# Put 4 objects into the list: 3 spheres and a plane (rf. class __init__ methods for parameters)
# center, radius, color(=RGB)
objs.append(Sphere(Vector(-2, 0, -10), 2.0, Vector(0, 255, 0)))
objs.append(Sphere(Vector(2, 0, -10),  3.5, Vector(255, 0, 0)))
objs.append(Sphere(Vector(0, -4, -10), 3.0, Vector(0, 0, 255)))
objs.append(Plane(Vector(0, 0, -12), Vector(0, 0, 1),
                  Vector(255, 255, 255)))  # point, normal, color

lightSource = Vector(10, 0, 0)  # light position
lightColor = Vector(255, 0, 0)  # light color

light = DirectionalLight(lightColor, 1, lightSource)

img = Image.new("RGB", (500, 500))
cameraPos = Vector(0, 0, 20)
for x in range(500):  # loop over all x values for our image
    print(x)   # provide some feedback to the user about our progress
    for y in range(500):  # loop over all y values
        ray = Ray(cameraPos, (Vector(x/50.0-5, y/50.0-5, 0)-cameraPos).normal())
        col = trace(ray, objs, light, 10)
        # print(col.x)
        # print(col.y)
        # print(col.z)
        img.putpixel((x, 499-y), gammaCorrection(col, GAMMA_CORRECTION))
        # time.sleep(5)
# save the image as a .png (or "BMP", but it produces a much larger file)
img.save("raytrace.png", "PNG")

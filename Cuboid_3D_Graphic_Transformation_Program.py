import pygame
import numpy as np
import sys

# Initializes all imported pygame modules
pygame.init()

# Window dimensions
wWidth, wHeight = 1071, 857
translationA = 4
rotationA = np.radians(2)
scalingA = 0.01

# X, Y, Z axis lines coordinates, with 4 entries to be able to do Translation
xyzPoints = np.array([
    [0, 0, 0, 1],
    [875, 0, 0, 1],
    [0, 450, 0, 1],
    [0, 0, 545, 1]
], dtype=float)

# Cuboid points or the coordinates of each corner
cboidX, cboidY, cboidZ = 100, 50, 40
cboidPoints = np.array([
    [-cboidX/1.1, -cboidY, -cboidZ/1.5, 1],
    [ cboidX/1.1, -cboidY, -cboidZ/1.5, 1],
    [ cboidX/1.1,  cboidY, -cboidZ/1.5, 1],
    [-cboidX/1.1,  cboidY, -cboidZ/1.5, 1],
    [-cboidX/1.1, -cboidY,  cboidZ/1.5, 1], 
    [ cboidX/1.1, -cboidY,  cboidZ/1.5, 1],
    [ cboidX/1.1,  cboidY,  cboidZ/1.5, 1], 
    [-cboidX/1.1,  cboidY,  cboidZ/1.5, 1] 
], dtype=float)

# For assigning from which corner the lines will connect to
cboidLines = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]


# The amount of rotation or tilt to get Isometric View
axZ = np.radians(0)
axX = np.radians(30)
axY = np.radians(-20)

#The matrices for applying the Isometric View
rotZ = np.array([
    [np.cos(axZ), -np.sin(axZ), 0, 0],
    [np.sin(axZ), np.cos(axZ), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])
rotX = np.array([
    [1, 0, 0, 0],
    [0, np.cos(axX), -np.sin(axX), 0],
    [0, np.sin(axX), np.cos(axX), 0],
    [0, 0, 0, 1]
])
rotY = np.array([
    [np.cos(axY), 0, np.sin(axY), 0],
    [0, 1, 0, 0],
    [-np.sin(axY), 0, np.cos(axY), 0],
    [0, 0, 0, 1]
])
IsoView = rotZ @ rotX @ rotY

# Identity matrix for projecting the objects
pIM = np.identity(4)
tX, tY, tZ = cboidX, cboidY, cboidZ
rX, rY, rZ = 0, 0, 0
sX, sY, sZ = 1.0, 1.0, 1.0

# Identity matrix for the transformations
mIM = np.identity(4)

# Function for projecting the x y z axis lines in the window in an isometric view
def project3Dto2D(p3D):
    
    p4D = np.dot(IsoView, p3D)

    projection = np.dot(pIM, p4D)

    x3D, y3D = projection[0], projection[1]
    
    centerX = wWidth // 5
    centerY = wHeight // 2
    
    windowX = int(x3D + centerX)
    windowY = int(centerY - y3D)
    
    return (windowX, windowY)
# Draws the x y z axis lines
def axis():
    # Calls the function that translates the z y z axis lines into isometric view
    projectedPs = [project3Dto2D(point) for point in xyzPoints]
    
    # Gets the resulting coordinates from the function
    origin = projectedPs[0]
    pXend = projectedPs[1]
    pYend = projectedPs[2]
    pZend = projectedPs[3]
    # Displays the axis lines
    pygame.draw.line(window, red, origin, pXend, 2)
    pygame.draw.line(window, green, origin, pYend, 2)
    pygame.draw.line(window, blue, origin, pZend, 2)

# Draws the cuboid object
def cuboid():
    isoCboid = np.dot(cboidPoints, mIM)

    iCboid = [project3Dto2D(point) for point in isoCboid]

    for corners in cboidLines:
        p1 = iCboid[corners[0]]
        p2 = iCboid[corners[1]]
        pygame.draw.line(window, white, p1, p2, 1)

# Translation Matrix:
# Moves the cuboid in 3D space by adding tx, ty, tz to all points.
# Uses a 4x4 matrix so it works with homogeneous coordinates.
def TM(tx, ty, tz):
    return np.array([
        [1, 0, 0, 0], 
        [0, 1, 0, 0], 
        [0, 0, 1, 0], 
        [tx, ty, tz, 1]
    ], dtype=float)

# Rotation Matrices (X, Y, Z):
# Rotates the cuboid around each axis using cosine and sine.
# These matrices change the orientation but not the size of the object.
def xRM(a):
    cos, sin = np.cos(a), np.sin(a)
    return np.array([
        [1, 0, 0, 0],
        [0, cos, -sin, 0],
        [0, sin, cos, 0],
        [0, 0, 0, 1]
    ], dtype=float)  
def yRM(a):
    cos, sin = np.cos(a), np.sin(a)
    return np.array([
        [cos, 0, sin, 0],
        [0, 1, 0, 0],
        [-sin, 0, cos, 0],
        [0, 0, 0, 1]
    ], dtype=float)  
def zRM(a):
    cos, sin = np.cos(a), np.sin(a)
    return np.array([
        [cos, -sin, 0, 0],
        [sin, cos, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype=float)  

# Scaling Matrix:
# Adjusts the size of the cuboid along the x, y, and z axes.
# Multiplies each axis by sx, sy, sz to stretch or shrink the object.
def SM(sx, sy, sz):
    return np.array([
        [sx, 0, 0, 0],
        [0, sy, 0, 0],
        [0, 0, sz, 0],
        [0, 0, 0, 1]
    ], dtype=float)

# Updates the model matrix(mIM) of the selected transformation
def upDmIM():
    global mIM

    tM = TM(tX, tY, tZ)

    rXM = xRM(rX)
    rYM = yRM(rY)
    rZM = zRM(rZ)

    sM = SM(sX, sY, sZ)

    rM = rXM @ rYM @ rZM

    mIM = rM @ tM @ sM

upDmIM()

# Resets the cuboid object
def reset():
    global tX, tY, tZ, rX, rY, rZ, sX, sY, sZ
    
    tX, tY, tZ = 100, 50, 40
    rX, rY, rZ = 0, 0, 0
    sX, sY, sZ = 1.0, 1.0, 1.0
    
    upDmIM()

# All the functions that will be called for each transformation
def tXadd(): global tX; tX += translationA; upDmIM()
def tXsub(): global tX; tX -= translationA; upDmIM()
def tYadd(): global tY; tY += translationA; upDmIM()
def tYsub(): global tY; tY -= translationA; upDmIM()
def tZadd(): global tZ; tZ += translationA; upDmIM()
def tZsub(): global tZ; tZ -= translationA; upDmIM()

def rXadd(): global rX; rX += rotationA; upDmIM()
def rXsub(): global rX; rX -= rotationA; upDmIM()
def rYadd(): global rY; rY += rotationA; upDmIM()
def rYsub(): global rY; rY -= rotationA; upDmIM()
def rZadd(): global rZ; rZ += rotationA; upDmIM()
def rZsub(): global rZ; rZ -= rotationA; upDmIM()

def sXadd(): global sX; sX += scalingA; upDmIM()
def sXsub(): global sX; sX -= scalingA; upDmIM()
def sYadd(): global sY; sY += scalingA; upDmIM()
def sYsub(): global sY; sY -= scalingA; upDmIM()
def sZadd(): global sZ; sZ += scalingA; upDmIM()
def sZsub(): global sZ; sZ -= scalingA; upDmIM()

# Colors used
bgC = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)

# Makes the window
window = pygame.display.set_mode((wWidth, wHeight))
# Sets the title at the top of the window
pygame.display.set_caption("Cuboid 3D Graphic Transformation Program")
# For the animation frames of the transformations 
fps = pygame.time.Clock()

run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                run = False
    
    # Detects keyboard clicks
    click = pygame.key.get_pressed()

    # Keys assigned for each transformation
    if click[pygame.K_SPACE]:
        reset()
    if click[pygame.K_d]:
        tXadd()
    if click[pygame.K_a]:
        tXsub()
    if click[pygame.K_w]:
        tYadd()
    if click[pygame.K_s]:
        tYsub()
    if click[pygame.K_q]:
        tZadd()
    if click[pygame.K_e]:
        tZsub()

    if click[pygame.K_t]:
        rXadd()
    if click[pygame.K_g]:
        rXsub()
    if click[pygame.K_f]:
        rYadd()
    if click[pygame.K_h]:
        rYsub()
    if click[pygame.K_r]:
        rZadd()
    if click[pygame.K_y]:
        rZsub()
    
    if click[pygame.K_l]:
        sXadd()
    if click[pygame.K_j]:
        sXsub()
    if click[pygame.K_i]:
        sYadd()
    if click[pygame.K_k]:
        sYsub()
    if click[pygame.K_u]:
        sZadd()
    if click[pygame.K_o]:
        sZsub()

    # Fills the window black
    window.fill(bgC)

    # All the texts in the window
    f = pygame.font.Font(None, 22)
    fAxis = pygame.font.Font(None, 40)
    X = fAxis.render("X", True, red)
    Y = fAxis.render("Y", True, green)
    Z = fAxis.render("Z", True, blue)

    window.blit(X, (1040, 567))
    window.blit(Y, (206, 10))
    window.blit(Z, (10, 686))


    t1 = f.render("TRANSLATE", True, white)
    t2 = f.render("-X = [A]     +X = [D]", True, white)
    t3 = f.render("-Y = [S]     +Y = [W]", True, white)
    t4 = f.render("-Z = [E]     +Z = [Q]", True, white)
    window.blit(t1, (947, 10))
    window.blit(t2, (930, 35))
    window.blit(t3, (930, 53))
    window.blit(t4, (930, 71))

    t5 = f.render("ROTATE", True, white)
    t6 = f.render("-X = [G]     +X = [T]", True, white)
    t7 = f.render("-Y = [H]     +Y = [F]", True, white)
    t8 = f.render("-Z = [Y]     +Z = [R]", True, white)
    window.blit(t5, (764, 10))
    window.blit(t6, (730, 35))
    window.blit(t7, (730, 53))
    window.blit(t8, (730, 71))

    t9 = f.render("SCALE", True, white)
    t10 = f.render("-X = [J]     +X = [L]", True, white)
    t11 = f.render("-Y = [K]     +Y = [I]", True, white)
    t12 = f.render("-Z = [O]     +Z = [U]", True, white)
    window.blit(t9, (567, 10))
    window.blit(t10, (530, 35))
    window.blit(t11, (530, 53))
    window.blit(t12, (530, 71))

    t13 = f.render("RESET = [SPACE]", True, white)
    t14 = f.render("EXIT = [BACKSPACE]", True, white)
    window.blit(t13, (930, 130))
    window.blit(t14, (900, 160))

    # Builds the axis lines
    axis()

    # Builds the cuboid
    cuboid()
            

    # Updates the window so we can see the changes to put it simply the transformations
    pygame.display.flip()

    fps.tick(60)
    
pygame.quit()
sys.exit()
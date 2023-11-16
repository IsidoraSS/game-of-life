import threading
import time

from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

brojIteracija = 10
velicinaMatrice=6
N = velicinaMatrice ** 2
usle = 0
condition = threading.Condition()

testMatrica=[[0,0,0,0,0,0],
             [0,1,1,0,0,0],
             [0,1,0,0,0,0],
             [0,0,0,0,1,0],
             [0,0,0,1,1,0],
             [0,0,0,0,0,0]]

class Celija(threading.Thread):
    def __init__(self, threadId, brojSuseda, stanje):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.brojSuseda = brojSuseda
        self.stanje = stanje
        self.brojSusedaKojiSuIscitali = 0
        self.lock = threading.Lock()
        self.brojIteracije = 0
        self.susedi = None

    def run(self):
        global usle, gameOfLife
        for x in range(brojIteracija):
            self.odradi()
            condition.acquire()
            usle += 1
            if not usle==N:
                condition.wait()
            else:
                usle=0
                napraviMatricu(gameOfLife, velicinaMatrice)
                condition.notifyAll()
            condition.release()

    def odradi(self):
        stanjeSuseda = []
        for sused in self.susedi:
            sused.lock.acquire()
            sused.brojSusedaKojiSuIscitali += 1
            stanjeSuseda.append(sused.stanje)
            sused.lock.release()
        while True:
            time.sleep(0.5)
            if self.brojSusedaKojiSuIscitali == self.brojSuseda:
                self.lock.acquire()
                self.brojSusedaKojiSuIscitali = 0
                self.stanje = self.izracunajStanje(stanjeSuseda)
                self.brojIteracije += 1
                self.lock.release()
                break
        print("ITERACIJA " + str(self.brojIteracije))

    def izracunajStanje(self, stanjeSuseda):
        brojZivihSuseda = stanjeSuseda.count(1)
        if (brojZivihSuseda < 2 or brojZivihSuseda > 3):
            return 0
        if (self.stanje == 1 and (brojZivihSuseda == 2 or brojZivihSuseda == 3)):
            return 1
        if (self.stanje == 0 and brojZivihSuseda == 3):
            return 1
        else:
            return 0




def brojSuseda(i,j,velicina):
    if (i==0 and j==0) or (i==0 and j==velicina-1) or (i==velicina-1 and j==0) or (i==velicina-1 and j==velicina-1):
        return 3
    if i==0 or j==0 or i==velicina-1 or j==velicina-1:
        return 5
    return 8


def vratiSusedePom(data, cell):
    row, col = cell[0], cell[1]
    row_max = len(data)
    col_max = len(data[0])

    return [data[row_d + row][col_d + col]
            for col_d in [-1, 0, 1]
            if (0 <= (col_d + col) < col_max) or (col_d == 0 and row_d == 0)
            for row_d in [-1, 0, 1]
            if 0 <= (row_d + row) < row_max]


def vratiSusede(matrica, i, j):
    susedi=vratiSusedePom(matrica,(i,j))
    susedi.remove(matrica[i][j])
    return susedi

listaMatrica = []
def napraviMatricu(matrica, velicinaMatrice):
    global listaMatrica
    novaMatrica = [[0 for x in range(velicinaMatrice)] for y in range(velicinaMatrice)]
    for i in range(velicinaMatrice):
        for j in range(velicinaMatrice):
            novaMatrica[i][j]=matrica[i][j].stanje
    listaMatrica.append(novaMatrica)


gameOfLife = [[0 for x in range(velicinaMatrice)] for y in range(velicinaMatrice)]
for i in range(velicinaMatrice):
    for j in range(velicinaMatrice):
        celija = Celija(str(i)+","+str(j), brojSuseda(i,j,velicinaMatrice),testMatrica[i][j])
        gameOfLife[i][j]=celija


for i in range(velicinaMatrice):
    for j in range(velicinaMatrice):
        gameOfLife[i][j].susedi=vratiSusede(gameOfLife,i,j)

for i in range(velicinaMatrice):
    for j in range(velicinaMatrice):
        gameOfLife[i][j].start()

for i in range(velicinaMatrice):
    for j in range(velicinaMatrice):
        gameOfLife[i][j].join()


for i in range(velicinaMatrice):
    for j in range(velicinaMatrice):
        gameOfLife[i][j].join()


def animate(steps):
    def init():
        im.set_data(steps[0])
        return [im]

    def animate(i):
        im.set_data(steps[i])
        return [im]

    im = plt.matshow(steps[0], interpolation='None', animated=True);

    anim = FuncAnimation(im.get_figure(), animate, init_func=init,
                         frames=len(steps), interval=500, blit=True, repeat=False);
    plt.show()
    return anim


anim = animate(listaMatrica)

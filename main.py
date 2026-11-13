import json, os, sys, urllib.request as U, urllib.error

ENV = os.environ.get('MAKEFUN_ENV_URL')
if not ENV:
    sys.exit('MAKEFUN_ENV_URL not set')


def post(path, body):
    q = U.Request(ENV + path, json.dumps(body).encode(), {'content-type': 'application/json'})
    try:
        with U.urlopen(q) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {'status': 'error', 'code': e.code}


PI = {'P': 1, 'N': 2, 'B': 3, 'R': 4, 'Q': 5, 'K': 6,
      'p': -1, 'n': -2, 'b': -3, 'r': -4, 'q': -5, 'k': -6}
VAL = (0, 100, 320, 330, 500, 900, 0)
KN = (14, 18, 31, 33, -31, -33, -14, -18)
BI = (15, 17, -15, -17)
RO = (16, -16, 1, -1)
KI = RO + BI
PROMO = {'q': 5, 'r': 4, 'b': 3, 'n': 2}
MATE = 100000
INF = 200000

PST = {
1: (0,0,0,0,0,0,0,0, 50,50,50,50,50,50,50,50, 10,10,20,30,30,20,10,10, 5,5,10,25,25,10,5,5,
    0,0,0,20,20,0,0,0, 5,-5,-10,0,0,-10,-5,5, 5,10,10,-20,-20,10,10,5, 0,0,0,0,0,0,0,0),
2: (-50,-40,-30,-30,-30,-30,-40,-50, -40,-20,0,0,0,0,-20,-40, -30,0,10,15,15,10,0,-30,
    -30,5,15,20,20,15,5,-30, -30,0,15,20,20,15,0,-30, -30,5,10,15,15,10,5,-30,
    -40,-20,0,5,5,0,-20,-40, -50,-40,-30,-30,-30,-30,-40,-50),
3: (-20,-10,-10,-10,-10,-10,-10,-20, -10,0,0,0,0,0,0,-10, -10,0,5,10,10,5,0,-10,
    -10,5,5,10,10,5,5,-10, -10,0,10,10,10,10,0,-10, -10,10,10,10,10,10,10,-10,
    -10,5,0,0,0,0,5,-10, -20,-10,-10,-10,-10,-10,-10,-20),
4: (0,0,0,0,0,0,0,0, 5,10,10,10,10,10,10,5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5,
    -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, -5,0,0,0,0,0,0,-5, 0,0,0,5,5,0,0,0),
5: (-20,-10,-10,-5,-5,-10,-10,-20, -10,0,0,0,0,0,0,-10, -10,0,5,5,5,5,0,-10,
    -5,0,5,5,5,5,0,-5, 0,0,5,5,5,5,0,-5, -10,5,5,5,5,5,0,-10,
    -10,0,5,0,0,0,0,-10, -20,-10,-10,-5,-5,-10,-10,-20),
6: (-30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30, -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30, -20,-30,-30,-40,-40,-30,-30,-20, -10,-20,-20,-20,-20,-20,-20,-10,
    20,20,0,0,0,0,20,20, 20,30,10,0,0,10,30,20),
}

POS = {}
for t in range(1, 7):
    tab = PST[t]
    w = [0] * 128
    b = [0] * 128
    for sq in range(128):
        if sq & 0x88:
            continue
        row, col = sq >> 4, sq & 7
        w[sq] = VAL[t] + tab[row * 8 + col]
        b[sq] = VAL[t] + tab[(7 - row) * 8 + col]
    POS[t] = (w, b)


def load(fen):
    f = fen.split()
    b = [0] * 128
    for r, row in enumerate(f[0].split('/')):
        c = 0
        for ch in row:
            if ch.isdigit():
                c += int(ch)
            else:
                b[16 * r + c] = PI[ch]
                c += 1
    white = f[1] == 'w'
    cr = f[2] if len(f) > 2 else ''
    ep = None
    if len(f) > 3 and f[3] != '-':
        ep = (8 - int(f[3][1])) * 16 + ord(f[3][0]) - 97
    return b, white, ep, cr


def u2m(u):
    return ((8 - int(u[1])) * 16 + ord(u[0]) - 97,
            (8 - int(u[3])) * 16 + ord(u[2]) - 97,
            PROMO.get(u[4], 0) if len(u) > 4 else 0)


def attacked(b, sq, byw):
    if byw:
        for o in (15, 17):
            p = sq + o
            if 0 <= p < 128 and not p & 0x88 and b[p] == 1:
                return True
    else:
        for o in (15, 17):
            p = sq - o
            if 0 <= p < 128 and not p & 0x88 and b[p] == -1:
                return True
    pc = 2 if byw else -2
    for o in KN:
        p = sq + o
        if 0 <= p < 128 and not p & 0x88 and b[p] == pc:
            return True
    kc = 6 if byw else -6
    for o in KI:
        p = sq + o
        if 0 <= p < 128 and not p & 0x88 and b[p] == kc:
            return True
    for o in RO:
        p = sq + o
        while 0 <= p < 128 and not p & 0x88:
            v = b[p]
            if v:
                if (v > 0) == byw and abs(v) in (4, 5):
                    return True
                break
            p += o
    for o in BI:
        p = sq + o
        while 0 <= p < 128 and not p & 0x88:
            v = b[p]
            if v:
                if (v > 0) == byw and abs(v) in (3, 5):
                    return True
                break
            p += o
    return False


def gen(b, white, ep, cr, caps=0):
    ms = []
    for f in range(128):
        v = b[f]
        if not v or (v > 0) != white:
            continue
        t = v if v > 0 else -v
        if t == 1:
            d = -16 if white else 16
            pro = 0 if white else 7
            start = 6 if white else 1
            p = f + d
            if not p & 0x88 and 0 <= p < 128 and not b[p]:
                if (p >> 4) == pro:
                    for pr in (5, 4, 3, 2):
                        ms.append((f, p, pr))
                elif not caps:
                    ms.append((f, p, 0))
                    if (f >> 4) == start:
                        q = f + 2 * d
                        if not q & 0x88 and 0 <= q < 128 and not b[q]:
                            ms.append((f, q, 0))
            for o in ((-15, -17) if white else (15, 17)):
                p = f + o
                if p & 0x88 or p < 0 or p > 127:
                    continue
                w = b[p]
                if w and (w > 0) != white:
                    if (p >> 4) == pro:
                        for pr in (5, 4, 3, 2):
                            ms.append((f, p, pr))
                    else:
                        ms.append((f, p, 0))
                elif ep is not None and p == ep and not w:
                    ms.append((f, p, 0))
        elif t == 2 or t == 6:
            for o in (KN if t == 2 else KI):
                p = f + o
                if p & 0x88 or p < 0 or p > 127:
                    continue
                w = b[p]
                if w:
                    if (w > 0) != white:
                        ms.append((f, p, 0))
                elif not caps:
                    ms.append((f, p, 0))
            if t == 6 and not caps:
                if white and f == 116:
                    if ('K' in cr and not b[117] and not b[118] and b[119] == 4
                            and not attacked(b, 116, False) and not attacked(b, 117, False)
                            and not attacked(b, 118, False)):
                        ms.append((116, 118, 0))
                    if ('Q' in cr and not b[115] and not b[114] and not b[113] and b[112] == 4
                            and not attacked(b, 116, False) and not attacked(b, 115, False)
                            and not attacked(b, 114, False)):
                        ms.append((116, 114, 0))
                elif not white and f == 4:
                    if ('k' in cr and not b[5] and not b[6] and b[7] == -4
                            and not attacked(b, 4, True) and not attacked(b, 5, True)
                            and not attacked(b, 6, True)):
                        ms.append((4, 6, 0))
                    if ('q' in cr and not b[3] and not b[2] and not b[1] and b[0] == -4
                            and not attacked(b, 4, True) and not attacked(b, 3, True)
                            and not attacked(b, 2, True)):
                        ms.append((4, 2, 0))
        else:
            for o in (RO if t == 4 else BI if t == 3 else KI):
                p = f + o
                while not p & 0x88 and 0 <= p < 128:
                    w = b[p]
                    if w:
                        if (w > 0) != white:
                            ms.append((f, p, 0))
                        break
                    if not caps:
                        ms.append((f, p, 0))
                    p += o
    return ms


def make(b, m, ep, cr):
    f, t, pr = m
    nb = b[:]
    v = nb[f]
    nb[f] = 0
    white = v > 0
    cap = nb[t]
    nb[t] = (pr if white else -pr) if pr else v
    if abs(v) == 1 and t == ep and not cap:
        nb[t + (16 if white else -16)] = 0
    if abs(v) == 6 and abs((t & 7) - (f & 7)) > 1:
        if t > f:
            nb[f + 1] = nb[f + 3]
            nb[f + 3] = 0
        else:
            nb[f - 1] = nb[f - 4]
            nb[f - 4] = 0
    nep = None
    if abs(v) == 1 and abs(t - f) == 32:
        nep = f - (16 if white else -16)
    ncr = cr
    if abs(v) == 6:
        ncr = ncr.replace('K' if white else 'k', '').replace('Q' if white else 'q', '')
    if f == 7 or t == 7:
        ncr = ncr.replace('k', '')
    if f == 0 or t == 0:
        ncr = ncr.replace('q', '')
    if f == 119 or t == 119:
        ncr = ncr.replace('K', '')
    if f == 112 or t == 112:
        ncr = ncr.replace('Q', '')
    return nb, nep, ncr


def ev(b):
    s = 0
    for sq in range(128):
        v = b[sq]
        if v:
            if v > 0:
                s += POS[v][0][sq]
            else:
                s -= POS[-v][1][sq]
    return s


class Stop(Exception):
    pass


nodes = 0
LIMIT = 200000
KILL = {}


def mscore(m, b, ep, ply):
    f, t, pr = m
    v = b[t]
    if pr:
        return 200000 + pr
    if v:
        return 100000 + (abs(v) if abs(v) < 6 else 0) * 100 - abs(b[f])
    if abs(b[f]) == 1 and t == ep:
        return 90000
    if m in KILL.get(ply, ()):
        return 80000
    return 0


def qs(b, white, ep, cr, alpha, beta, ply):
    global nodes
    nodes += 1
    if nodes > LIMIT:
        raise Stop
    k = -6 if white else 6
    if k not in b:
        return -MATE + ply
    st = ev(b) if white else -ev(b)
    if st >= beta:
        return st
    if st > alpha:
        alpha = st
    ms = gen(b, white, ep, cr, 1)
    ms.sort(key=lambda m: mscore(m, b, ep, ply), reverse=True)
    for m in ms:
        nb, ne, nc = make(b, m, ep, cr)
        s = -qs(nb, not white, ne, nc, -beta, -alpha, ply + 1)
        if s > alpha:
            alpha = s
            if alpha >= beta:
                return alpha
    return alpha


def nega(b, white, ep, cr, d, alpha, beta, ply):
    global nodes
    nodes += 1
    if nodes > LIMIT:
        raise Stop
    k = 6 if white else -6
    if k not in b:
        return -MATE + ply
    if d <= 0:
        return qs(b, white, ep, cr, alpha, beta, ply)
    incheck = attacked(b, b.index(k), not white)
    if incheck:
        d += 1
    ms = gen(b, white, ep, cr)
    ms.sort(key=lambda m: mscore(m, b, ep, ply), reverse=True)
    best = -INF
    any_ = False
    for m in ms:
        nb, ne, nc = make(b, m, ep, cr)
        any_ = True
        s = -nega(nb, not white, ne, nc, d - 1, -beta, -alpha, ply + 1)
        if s > best:
            best = s
        if s > alpha:
            alpha = s
        if alpha >= beta:
            if not b[m[1]]:
                KILL.setdefault(ply, [])
                KILL[ply] = [m] + [x for x in KILL[ply] if x != m][:1]
            break
    if not any_:
        return (-MATE + ply) if incheck else 0
    return best


def choose(fen, legal, budget=200000):
    global nodes, LIMIT, KILL
    KILL = {}
    b, white, ep, cr = load(fen)
    rootm = []
    lut = {}
    for u in legal:
        m = u2m(u)
        if m not in lut:
            lut[m] = u
            rootm.append(m)
    best = legal[0]
    bestm = rootm[0]
    nodes = 0
    LIMIT = budget
    for d in range(1, 30):
        a = -INF
        cur = None
        hit = False
        order = [bestm] + [m for m in rootm if m != bestm]
        try:
            for m in order:
                nb, ne, nc = make(b, m, ep, cr)
                s = -nega(nb, not white, ne, nc, d - 1, -INF, -a, 1)
                if s > a:
                    a = s
                    cur = m
        except Stop:
            hit = True
        if cur is not None:
            best = lut[cur]
            bestm = cur
        if hit:
            break
    return best


while True:
    g = post('/game', {})
    if g.get('status') == 'done':
        break
    while g.get('status') == 'your_move':
        mv = choose(g['fen'], g['legal_moves'])
        g = post('/move', {'game': g['game'], 'move': mv})
    print('game %s: %s by %s' % (g.get('game'), g.get('outcome'), g.get('reason')), file=sys.stderr)
print('done: %s won, %s drawn, %s lost' % (g.get('wins'), g.get('draws'), g.get('losses')), file=sys.stderr)

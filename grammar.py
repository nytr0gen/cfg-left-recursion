class Grammar:
    EPSILON = '#'

    def __init__(self, start, raw):
        self._raw = raw.strip()
        self.start = start
        self.productions = dict()
        for line in self._raw.split('\n'):
            if line == '': continue

            l, r = map(lambda x: x.strip(),
                       line.split('->'))
            if l in self.productions:
                self.productions[l].append(r)
            else:
                self.productions[l] = [r]

    def _is_non_terminal(self, l):
        return l in self.productions

    @property
    def _non_terminals(self):
        return self.productions.keys()

    @property
    def _next_letter(self):
        for i in range(65, 91):
            l = chr(i)
            if not self._is_non_terminal(l):
                return l

        raise ValueError('No more non terminals left')

    def _is_direct_left_recursive(self, l):
        for r in self.productions[l]:
            if r.startswith(l):
                return True

        return False

    def is_left_recursive(self):
        for l in self._non_terminals:
            if self._is_direct_left_recursive(l):
                return True

        return False

    def _remove_direct_left_recursion(self, l):
        if not self._is_direct_left_recursive(l):
            return

        ls = self._next_letter
        new_prod = []
        prod = []
        for r in self.productions[l]:
            if r.startswith(l):  # direct left recursion
                new_prod.append(r[1:] + ls)
            elif r == self.EPSILON:
                prod.append(ls)
            else:
                prod.append(r + ls)

        if len(prod) == 0:
            prod.append(ls)
        else:
            new_prod.append(self.EPSILON)

        self.productions[l] = prod
        self.productions[ls] = new_prod

    def remove_direct_left_recursion(self):
        prods = []
        for l in self._non_terminals:
            if self._is_direct_left_recursive(l):
                prods.append(l)

        for l in prods:
            self._remove_direct_left_recursion(l)

    def remove_all_left_recursion(self):
        A = list(self._non_terminals)
        A.sort()
        # for each non terminal Ai
        for i, Ai in enumerate(A):
            # self.print_productions()
            # print('Urmeaza %s' % Ai)
            # print('')
            changed = True
            # repeat until iteration leaves grammar unchanged
            while changed:
                changed = False
                # for each rule Ai -> alpha_i, alpha_i - sequeunce terminals nonterminals
                for alpha_i in list(self.productions[Ai]):
                    # if alpha_i begins with a nonterminal Aj and j <i
                    Aj = alpha_i[0]
                    try:
                        j = A.index(Aj)
                        if not (j < i):
                            continue
                    except ValueError:
                        # not self._is_non_terminal(Aj)
                        # index not found
                        continue

                    changed = True

                    # let beta_i be alpha_i[1:]
                    beta_i = alpha_i[1:]

                    # remove the rule Ai -> alpha_i
                    self.productions[Ai].remove(alpha_i)

                    # for each rule Aj -> alpha_j
                    for alpha_j in self.productions[Aj]:
                        # add the rule Ai -> alpha_j + beta_i
                        self.productions[Ai].append(alpha_j + beta_i)

            # remove direct left recursion in Ai
            self._remove_direct_left_recursion(Ai)

    def print_productions(self):
        l = self.start
        r = self.productions[l]
        print('%s -> %s' % (l, ' | '.join(r)))

        for l, r in self.productions.items():
            if l == self.start: continue
            print('%s -> %s' % (l, ' | '.join(r)))

    def compute_first_k(self, k, word):
        res = set()
        if len(word) == 0:
            return set()
        elif k == 0:
            return set()

        l = word[0]
        if self._is_non_terminal(l):
            for r in self.productions[l]:
                if r == self.EPSILON:
                    t = word[1:]
                else:
                    t = r + word[1:]

                res |= self.compute_first_k(k, t)
        else:
            res = set(
                l + x
                for x in self.compute_first_k(k-1, word[1:])
            )
            if len(res) == 0:
                res.add(l)

        return res

    follow_sets = {}
    def _compute_follow_k(self, k, w):
        self.follow_sets[w] = self.follow_sets.get(w, set())
        for l in self._non_terminals:
            for r in self.productions[l]:
                idx = r.find(w)
                if idx == -1: continue

                rs = r[idx + 1:]  # production sliced after nonterminal
                for f in self.follow_sets.get(l, []):
                    self.follow_sets[w] |= self.compute_first_k(k, rs + f)

        return self.follow_sets[w]

    def compute_follow_k(self, k):
        self.follow_sets = {
            self.start: set('$')
        }
        for _ in range(10):  # hack so i dont have to check if the sets have changed
            for w in self._non_terminals:
                self._compute_follow_k(k, w)


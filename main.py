from grammar import Grammar

start = input().strip()
raw = ''
while True:
    try:
        raw += input() + '\n'
    except EOFError:
        break

g = Grammar(start, raw)
g.print_productions()

ans = 'da' if g.is_left_recursive() else 'nu'
print('Este recursiva la stanga: %s' % ans)
print('')

print('Eliminam recursivitatea la stanga')
g.remove_all_left_recursion()
g.print_productions()

ans = 'da' if g.is_left_recursive() else 'nu'
print('Este recursiva la stanga: %s' % ans)
print('')

k = 3
for w in ['ETF']:
    print('multimile first_k(%s): ' % w, end='')
    print(g.compute_first_k(k, w))


g.compute_follow_k(k)
for l in g._non_terminals:
    print('multimile follow_k(%s): ' % l, end='')
    print(g.follow_sets[l])

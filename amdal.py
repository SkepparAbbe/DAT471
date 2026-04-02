def amdal(p, n):
    return 1/(1-p+(p/n))

ns = [2^n for n in range(2,6)]
print(ns)

# for number in ns:
#     print(f"{number} of processors gives {amdal(0.7, number)} speed up")
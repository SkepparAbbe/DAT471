def amdal(p, n):
    return 1/(1-p+(p/n))

ns = [2**n for n in range(1,6)]

for number in ns:
    print(f"{number} processors gives {amdal(0.7, number):.2f} speedup")
    
print(f"\nThe maximum theoretical limit is: {1/(1-0.7):.2f}")

word_counts = {
    "result": 1,
    "is": 18,
    "output": 7,
    "analysis": 19,
    "key": 12,
    "fast": 7,
    "count": 6,
    "system": 3,
    "code": 15,
    "simple": 8,
    "user": 4,
    "script": 10,
    "and": 31,
    "learning": 9,
    "python": 28,
    "example": 5,
    "dictionary": 14,
    "value": 12,
    "the": 42,
    "data": 25
}

print(sorted(word_counts.items(), key=lambda item: item[1], reverse=True)[:10])

sum = 0
for word, cnt in word_counts.items():
    sum += len(word) * cnt

print(sum)
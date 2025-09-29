import matplotlib.pyplot as plt

givens = [
    [5,3,0, 0,7,0, 0,0,0],
    [6,0,0, 1,9,5, 0,0,0],
    [0,9,8, 0,0,0, 0,6,0],
    [8,0,0, 0,6,0, 0,0,3],
    [4,0,0, 8,0,3, 0,0,1],
    [7,0,0, 0,2,0, 0,0,6],
    [0,6,0, 0,0,0, 2,8,0],
    [0,0,0, 4,1,9, 0,0,5],
    [0,0,0, 0,8,0, 0,7,9],
]

fig, ax = plt.subplots(figsize=(6,6))
ax.set_xlim(0,9)
ax.set_ylim(0,9)

# Draw grid
for i in range(10):
    lw = 2 if i % 3 == 0 else 0.5
    ax.axhline(i, color="black", lw=lw)
    ax.axvline(i, color="black", lw=lw)

# Fill numbers
for r in range(9):
    for c in range(9):
        val = givens[r][c]
        if val != 0:
            ax.text(c+0.5, 8.5-r, str(val), va="center", ha="center", fontsize=14)

ax.axis("off")
plt.show()

# store as PNG in /images folder
fig.savefig("images/sudoku_image.png", bbox_inches="tight")

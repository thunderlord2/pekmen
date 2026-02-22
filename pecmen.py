import curses
import time
import random
import requests

# =============================
# CONFIG
# =============================

SERVER_URL = "https://your-app-name.onrender.com/submit"
NUM_FOOD = 10
tile_width = 3

# =============================
# MAZE LAYOUT
# =============================

maze_layout = [
    "============",
    "!          !",
    "! ──     ──!",
    "!          !",
    "!   ──  ── !",
    "!          !",
    "! ──       !",
    "!          !",
    "!   ──  ── !",
    "!          !",
    "!     ──   !",
    "============",
]

player_y, player_x = 1, 1
direction = 1  # 1 = right, 0 = left
best_time = float("inf")  # global best only

# =============================
# MAZE EXPANSION
# =============================

def expand_maze(layout):
    expanded = []
    rows = len(layout)
    cols = len(layout[0])
    for r, row in enumerate(layout):
        new_row = ""
        for c, ch in enumerate(row):
            if r == 0 and c == 0:
                new_row += "╔"
            elif r == 0 and c == cols - 1:
                new_row += "╗"
            elif r == rows - 1 and c == 0:
                new_row += "╚"
            elif r == rows - 1 and c == cols - 1:
                new_row += "╝"
            elif (r == 0 or r == rows - 1) and (0 < c < cols - 1):
                new_row += "═" * tile_width
            elif (c == 0 or c == cols - 1) and (0 < r < rows - 1):
                new_row += "║"
            elif ch == "─":
                new_row += "─" * tile_width
            elif ch == " ":
                new_row += " " * tile_width
            else:
                new_row += ch * tile_width
        expanded.append(new_row)
    return expanded


maze = expand_maze(maze_layout)
height = len(maze)
width = len(maze[0])

def logical_to_expanded(y, x):
    return (y, 1 + x * tile_width)

# =============================
# FOOD GENERATION
# =============================

walkable_tiles = []
rows = len(maze_layout)
cols = len(maze_layout[0])

for row_idx, row in enumerate(maze_layout):
    for col_idx, ch in enumerate(row):
        if row_idx == 0 or row_idx == rows - 1:
            continue
        if col_idx == 0 or col_idx >= cols - 2:
            continue
        if ch == " " and row[col_idx - 1] != "─" and row[col_idx + 1] != "─":
            walkable_tiles.append((row_idx, col_idx))

random_food_logical = random.sample(walkable_tiles, min(NUM_FOOD, len(walkable_tiles)))
food_positions = set(logical_to_expanded(y, x) for y, x in random_food_logical)

# =============================
# MAIN GAME LOOP
# =============================

def main(stdscr):
    global player_x, player_y, direction, best_time

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    move_delay = 0.15
    last_move_time = 0

    start_time = time.time()
    foods = set(food_positions)

    while True:
        stdscr.clear()

        max_y, max_x = stdscr.getmaxyx()

        # Draw maze
        for idx, row in enumerate(maze):
            stdscr.addstr(idx, 0, row)

        # Draw food
        for fy, fx in foods:
            stdscr.addstr(fy, fx, "*")

        # Draw player
        sprite = ".<." if direction else ".>."
        stdscr.addstr(player_y, player_x, sprite)

        # Draw timer below maze
        elapsed = time.time() - start_time
        seconds = int(elapsed)
        milliseconds = int((elapsed - seconds) * 1000)
        timer_text = f"Time: {seconds:02}.{milliseconds:03}"
        stdscr.addstr(height + 1, 0, timer_text)

        # Draw global best time
        if best_time != float("inf"):
            best_seconds = int(best_time)
            best_millis = int((best_time - best_seconds) * 1000)
            best_text = f"Best: {best_seconds:02}.{best_millis:03}"
            stdscr.addstr(height + 2, 0, best_text)

        stdscr.refresh()

        now = time.time()
        key = stdscr.getch()

        if key != -1 and now - last_move_time > move_delay:
            new_y, new_x = player_y, player_x

            if key == curses.KEY_LEFT:
                cand_x = player_x - tile_width
                if cand_x >= 0 and all(t not in "═║─│╔╗╚╝" for t in maze[player_y][cand_x:cand_x+tile_width]):
                    new_x = cand_x
                    direction = 0

            elif key == curses.KEY_RIGHT:
                cand_x = player_x + tile_width
                if cand_x + tile_width <= width and all(t not in "═║─│╔╗╚╝" for t in maze[player_y][cand_x:cand_x+tile_width]):
                    new_x = cand_x
                    direction = 1

            elif key == curses.KEY_UP:
                cand_y = player_y - 1
                if cand_y >= 0 and all(t not in "═║─│╔╗╚╝" for t in maze[cand_y][player_x:player_x+tile_width]):
                    new_y = cand_y

            elif key == curses.KEY_DOWN:
                cand_y = player_y + 1
                if cand_y < height and all(t not in "═║─│╔╗╚╝" for t in maze[cand_y][player_x:player_x+tile_width]):
                    new_y = cand_y

            elif key == ord("q"):
                break

            player_x, player_y = new_x, new_y

            # Check food collection
            for offset in range(3):
                if (player_y, player_x + offset) in foods:
                    foods.remove((player_y, player_x + offset))

            # =============================
            # GAME COMPLETE
            # =============================
            if not foods:
                total_time = time.time() - start_time

                # Send to global server only
                try:
                    response = requests.post(
                        SERVER_URL,
                        json={"time": total_time},
                        timeout=2
                    )

                    if response.status_code == 200:
                        data = response.json()
                        server_best = data.get("best")
                        if server_best:
                            best_time = server_best

                except requests.exceptions.RequestException:
                    pass

                break

            last_move_time = now

        time.sleep(0.01)

curses.wrapper(main)
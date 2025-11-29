import random
import numpy
import curses

BoardSize = 4

#board functions
def leftShift(Row):
    Row = Row.copy()
    if Row[0] == 0:
        NonZero = -1
    else:
        NonZero = 0
    for i in range(1, len(Row)):
        if Row[i] != 0:
            if NonZero == -1:
                Row[0] = Row[i]
                Row[i] = 0
                NonZero = 0
            elif (Row[NonZero] == Row[i]) and (type(Row[NonZero]) == type(Row[i])):
                Row[NonZero] = f'{2*Row[NonZero]}' 
                Row[i] = 0
            else:
                Row[NonZero + 1] = Row[i]
                if NonZero + 1 != i:
                    Row[i] = 0
                NonZero += 1
    return [int(x) for x in Row]

def Shift(Matrix, Direction):
    Matrix = numpy.array(Matrix, dtype = int)
    Reverse = numpy.array([[1 if j == BoardSize - 1 - i else 0 for j in range(BoardSize)] for i in range(BoardSize)])
    match Direction:
        case 'L':
            Matrix = [leftShift(i) for i in Matrix]
        case 'R':
            Matrix = Matrix @ Reverse
            Matrix = [leftShift(i) for i in Matrix]
            Matrix = Matrix @ Reverse
        case 'U':
            Matrix = numpy.transpose(Matrix)
            Matrix = [leftShift(i) for i in Matrix]
            Matrix = numpy.transpose(Matrix)
        case 'D':
            Matrix = numpy.transpose(Matrix)
            Matrix = Matrix @ Reverse
            Matrix = [leftShift(i) for i in Matrix]
            Matrix = Matrix @ Reverse
            Matrix = numpy.transpose(Matrix)
    return numpy.array(Matrix)

def ReplaceZeroes(Matrix):
    Matrix = Matrix.copy()
    Zeroes = []
    for i in range(BoardSize):
        for j in range(BoardSize):
            if Matrix[i][j] == 0:
                Zeroes.append([i,j])
    if len(Zeroes) > 0:
        Zeroes = Zeroes[random.randint(0,len(Zeroes)-1)]
        Matrix[Zeroes[0]][Zeroes[1]] = 2*random.randint(1,2)
        return numpy.array(Matrix)
    else:
        return False

def FindEquals(Matrix):
    for i in range(BoardSize):
        for j in range(BoardSize):
            if i+1 != BoardSize:
                if Matrix[i][j] == Matrix[i+1][j]:
                    return True
            if j+1 != BoardSize:
                if Matrix[i][j] == Matrix[i][j+1]:
                    return True
    return False

#display functions
def get_color(value):
    match value:
        case 0:
            return curses.color_pair(6)
        case 2048:
            return curses.color_pair(7)
        case _:
            return curses.color_pair(((int(numpy.log2(value)) - 1) % 5) + 1)

def draw_board(stdscr, matrix):
    stdscr.clear()
    scr_h, scr_w = stdscr.getmaxyx()
    
    title = "2048 : Arrow / WASD Keys to Move, Q to Quit"
    stdscr.addstr(1, (scr_w - len(title)) // 2, title, curses.A_BOLD)

    cell_w = 8
    start_y = (scr_h // 2) - (BoardSize * 2) // 2
    start_x = (scr_w // 2) - (BoardSize * (cell_w + 1)) // 2

    for i in range(BoardSize):
        separate = ('-' * cell_w + '+') * (BoardSize - 1) + '-' * cell_w
        stdscr.addstr(start_y + (i * 2), start_x, separate)
        
        for j in range(BoardSize):
            val = matrix[i][j]
            val_str = str(val) if val != 0 else "."
            pos_x = start_x + (j * (cell_w + 1))
            padding = (cell_w - len(val_str)) // 2
            stdscr.addstr(start_y + (i * 2) + 1, pos_x, " " * cell_w)
            stdscr.addstr(start_y + (i * 2) + 1, pos_x + padding, val_str, get_color(val) | curses.A_BOLD)
            
            if j < BoardSize - 1:
                stdscr.addstr(start_y + (i * 2) + 1, pos_x + cell_w, "|")
    
    separate = ('-' * cell_w + '+') * (BoardSize - 1) + '-' * cell_w
    stdscr.addstr(start_y + (BoardSize * 2), start_x, separate)
    stdscr.refresh()


#game loop
def main(stdscr):

    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE,curses.COLOR_YELLOW)

    Grid = numpy.array([[0 for y in range(BoardSize)] for x in range(BoardSize)])
    position1 = (random.randint(0,BoardSize - 1), random.randint(0,BoardSize - 1))
    position2 = (random.randint(0,BoardSize - 1), random.randint(0,BoardSize - 1))
    while position1 == position2:
        position2 = (random.randint(0,BoardSize - 1), random.randint(0,BoardSize - 1))
    Grid[position1[0]][position1[1]] = 2*random.randint(1,2)
    Grid[position2[0]][position2[1]] = 2*random.randint(1,2)

    game_over = "GAME OVER! (Press any key to exit)"
    game_win = "WINNER! (Press any key to exit)"
        

    while True:
        draw_board(stdscr, Grid)

        key = stdscr.getch()
        direction = None
        if key == curses.KEY_UP or key == ord('w') or key == ord('W'):
            direction = 'U'
        elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
            direction = 'D'
        elif key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
            direction = 'L'
        elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
            direction = 'R'
        elif key == ord('q') or key == ord('Q'):
            break

        if direction:
            store_grid = Shift(Grid, direction)
            if not numpy.array_equal(Grid, store_grid):
                Grid = store_grid
                StoreGrid = ReplaceZeroes(Grid)
                
                if isinstance(StoreGrid, numpy.ndarray):
                    Grid = StoreGrid
                    scr_h, scr_w = stdscr.getmaxyx()

                    if 2048 in Grid:
                        draw_board(stdscr, Grid)
                        stdscr.addstr(scr_h//2 + 6, (scr_w-len(game_win))// 2, game_win, curses.color_pair(6) | curses.A_BOLD)
                        stdscr.getch()
                        break

                    if not (numpy.any(Grid == 0) or FindEquals(Grid)):
                        draw_board(stdscr, Grid)
                        stdscr.addstr(scr_h//2 + 6, (scr_w-len(game_over))// 2, game_over, curses.color_pair(6) | curses.A_BOLD)
                        stdscr.getch()
                        break
                else:
                    if not FindEquals(Grid):
                        draw_board(stdscr, Grid)
                        stdscr.addstr(scr_h//2 + 6, (scr_w-len(game_over))// 2, game_over, curses.color_pair(6) | curses.A_BOLD)
                        stdscr.getch()
                        break

curses.wrapper(main)
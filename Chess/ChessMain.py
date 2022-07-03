import pygame
from ChessEngine import ChessBoard, Move

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT / DIMENSION
FPS = 20
IMAGES = {}


def loadImages():
    pieces = ['wK', 'bK', 'wN', 'bN', 'wB', 'bB', 'bR', 'wR', 'wp', 'bQ', 'bp', 'wQ']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.scale(pygame.image.load('Chess_images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


def main():
    # game initialization and screen creation
    pygame.init()
    screen = pygame.display.set_mode((HEIGHT, WIDTH))
    pygame.display.set_caption("Chess Game")
    clock = pygame.time.Clock()
    cb = ChessBoard()
    validMoves = cb.getValidMoves()
    moveMade = False

    loadImages()  # only do this once before while loop so as to avoid slowing down the script
    sqSelected = ()  # keep track of the last click made by the player
    playerClicks = []  # keep track of player clicks - for making moves

    running = True
    # creation of game loop
    while running:
        clock.tick(FPS)
        # process input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # mouse handler
            elif event.type == pygame.MOUSEBUTTONDOWN:
                location = pygame.mouse.get_pos()  # (x, y) location of mouse
                col = int(location[0] // SQ_SIZE)
                row = int(location[1] // SQ_SIZE)

                if sqSelected == (row, col):
                    # unselect the cell if the player click on the same cell as before
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)

                if len(playerClicks) == 2:
                    userMove = Move(playerClicks[0], playerClicks[1], cb.board)
                    for move in validMoves:
                        if userMove == move:  # designed for enpassant, as an userMove can never be an 'enpassantMove'
                            cb.makeMove(move)
                            moveMade = True

                    sqSelected = ()
                    playerClicks = []
            # key handler
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    cb.undoMove()
                    moveMade = True

        if moveMade:
            # print(cb.currentCastlingRight.wks, cb.currentCastlingRight.wqs)
            validMoves = cb.getValidMoves()
            moveMade = False

        # render
        drawGameState(screen, cb, sqSelected)
        pygame.display.update()

    pygame.quit()


def drawGameState(screen, gs, sqSelected):
    drawBoard(screen)
    drawPieces(screen, gs, gs.board, sqSelected)


def drawBoard(screen):
    # draw squares on the board
    colors = [pygame.Color('white'), pygame.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            pygame.draw.rect(screen, colors[(r + c) % 2], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, gs, board, sqSelected):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if sqSelected != () and board[sqSelected[0]][sqSelected[1]] != '--':
        pygame.draw.rect(screen, (pygame.Color('yellow')),
                         pygame.Rect(sqSelected[1] * SQ_SIZE, sqSelected[0] * SQ_SIZE, SQ_SIZE, SQ_SIZE), 3)

        side = board[sqSelected[0]][sqSelected[1]][0]
        piece = board[sqSelected[0]][sqSelected[1]][1]
        moves = []
        turn = 'w' if gs.whiteToMove else 'b'
        if side == turn:
            moves = gs.moveFunctions[piece](sqSelected[0], sqSelected[1], moves)

        for move in moves:
            destRow, destCol = move.end
            pygame.draw.rect(screen, (pygame.Color('blue')),
                             pygame.Rect(destCol * SQ_SIZE, destRow * SQ_SIZE, SQ_SIZE, SQ_SIZE), 3)

    if gs.blackKingInCheck:
        pygame.draw.rect(screen, (pygame.Color('red')),
                         pygame.Rect(gs.blackKingPosition[1] * SQ_SIZE, gs.blackKingPosition[0] * SQ_SIZE,
                                     SQ_SIZE, SQ_SIZE), 5)

    if gs.whiteKingInCheck:
        pygame.draw.rect(screen, (pygame.Color('red')),
                         pygame.Rect(gs.whiteKingPosition[1] * SQ_SIZE, gs.whiteKingPosition[0] * SQ_SIZE,
                                     SQ_SIZE, SQ_SIZE), 5)


if __name__ == '__main__':
    main()

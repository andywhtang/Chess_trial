from copy import deepcopy


class ChessBoard:
    def __init__(self):
        self.whiteToMove = True
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        """self.board = [
            ['--', '--', '--', '--', '--', '--', '--', 'bK'],
            ['--', '--', '--', '--', '--', 'wK', '--', '--'],
            ['--', '--', '--', '--', '--', '--', 'wQ', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', 'wp', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--']
        ]"""
        self.moveLog = []
        self.moveCount = 1
        self.moveFunctions = {
            'K': self.getKingMoves, 'Q': self.getQueenMoves, 'R': self.getRookMoves,
            'N': self.getKnightMoves, 'B': self.getBishopMoves, 'p': self.getPawnMoves,
        }
        self.blackKingInCheck = False
        self.whiteKingInCheck = False
        self.currentCastlingRight = CastlingRights(True, True, True, True)
        self.castlingRightsLog = [deepcopy(self.currentCastlingRight)]

        self.blackKingPosition = None
        self.whiteKingPosition = None
        self.checkmate = False
        self.stalemate = False

        self.enpassantPossible = ()  # Coordinates where enpassant is possible
        self.updateKingPosition()

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        self.moveCount += 1

        # pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        # update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.endRow - move.startRow) == 2:
            self.enpassantPossible = ((move.endRow + move.startRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        # update castling rights:
        self.updateCastleRights(move)
        self.castlingRightsLog.append(CastlingRights(self.currentCastlingRight.wqs, self.currentCastlingRight.wks,
                                                     self.currentCastlingRight.bqs, self.currentCastlingRight.bks))

        # castling
        if move.isCastling:
            self.board[move.startRow][3 if move.endCol == 2 else 5] = move.pieceMoved[0] + 'R'
            self.board[move.startRow][0 if move.endCol == 2 else 7] = '--'

        self.checkCheck()
    """
    Undo the last move made
    """
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured

            self.moveCount -= 1
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undoing a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.endRow - move.startRow) == 2:
                self.enpassantPossible = ()

            self.castlingRightsLog.pop()
            self.currentCastlingRight = deepcopy(self.castlingRightsLog[-1])

            if move.isCastling:
                self.board[move.startRow][0 if move.endCol == 2 else 7] = move.pieceMoved[0] + 'R'
                self.board[move.startRow][3 if move.endCol == 2 else 5] = '--'

            self.checkCheck()
            self.whiteToMove = not self.whiteToMove
    """
    All moves considering checks
    """
    def getValidMoves(self):
        # print(self.currentCastlingRight.wks, self.currentCastlingRight.wqs)
        moves = self.getAllPossibleMoves()
        tempEnpassantPossible = self.enpassantPossible

        for move in moves[::-1]:
            self.makeMove(move)
            if (not self.whiteToMove and self.whiteKingInCheck) or (self.whiteToMove and self.blackKingInCheck):
                moves.remove(move)
            self.undoMove()

        if len(moves) == 0:
            if self.whiteToMove and self.whiteKingInCheck:
                self.checkmate = True
                print('black won!')
            elif not self.whiteToMove and self.blackKingInCheck:
                self.checkmate = True
                print('white won!')
            else:
                self.stalemate = True
                print('stalemate!')

        self.enpassantPossible = tempEnpassantPossible
        # print(self.currentCastlingRight.wks, self.currentCastlingRight.wqs)
        return moves

    def squareUnderAttack(self, square, side):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                color = self.board[r][c][0]
                piece = self.board[r][c][1]
                if side == color:
                    self.moveFunctions[piece](r, c, moves)

        for move in moves:
            if square == move.end:
                return True

        return False

    def checkCheck(self):
        self.updateKingPosition()
        self.whiteKingInCheck = self.squareUnderAttack(self.whiteKingPosition, 'b')
        self.blackKingInCheck = self.squareUnderAttack(self.blackKingPosition, 'w')

    """
    All moves without considering checks
    """
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    def updateCastleRights(self, move):
        if not self.castlingRightsLog[-1].wks:
            self.currentCastlingRight.wks = False
        if not self.castlingRightsLog[-1].wqs:
            self.currentCastlingRight.wqs = False
        if not self.castlingRightsLog[-1].bks:
            self.currentCastlingRight.bks = False
        if not self.castlingRightsLog[-1].bqs:
            self.currentCastlingRight.bqs = False

        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

        if move.pieceCaptured == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    def getKingMoves(self, r, c, moves):
        moves.extend([Move((r, c), (i, j), self.board)
                      for i in range(8) for j in range(8)
                      if (abs(r - i) <= 1) and (abs(c - j) <= 1) and
                      self.board[i][j][0] != self.board[r][c][0]])

        if c == 4:
            if r == 0 and not self.blackKingInCheck:
                if self.board[r][0] == 'bR' and self.board[r][1] == '--' and self.board[r][2] == '--' \
                        and self.board[r][3] == '--' and self.currentCastlingRight.bqs and \
                        not self.squareUnderAttack((r, 3), 'w'):
                    moves.append(Move((r, c), (r, c - 2), self.board))
                if self.board[r][7] == 'bR' and self.board[r][6] == '--' and self.board[r][5] == '--' \
                        and self.currentCastlingRight.bks and not self.squareUnderAttack((r, 5), 'w'):
                    moves.append(Move((r, c), (r, c + 2), self.board))
            elif r == 7 and not self.whiteKingInCheck:
                if self.board[r][0] == 'wR' and self.board[r][1] == '--' and self.board[r][2] == '--' \
                        and self.board[r][3] == '--' and self.currentCastlingRight.wqs and \
                        not self.squareUnderAttack((r, 3), 'b'):
                    moves.append(Move((r, c), (r, c - 2), self.board))
                if self.board[r][7] == 'wR' and self.board[r][6] == '--' and self.board[r][5] == '--' \
                        and self.currentCastlingRight.wks and not self.squareUnderAttack((r, 5), 'b'):
                    moves.append(Move((r, c), (r, c + 2), self.board))
        return moves

    def getQueenMoves(self, r, c, moves):
        moves = self.getBishopMoves(r, c, moves)
        moves = self.getRookMoves(r, c, moves)
        return moves

    def getRookMoves(self, r, c, moves):
        row = r - 1
        turn = self.board[r][c][0]
        while row >= 0:
            if self.board[row][c][0] == turn:
                break
            elif self.board[row][c][0] != '-':
                moves.append(Move((r, c), (row, c), self.board))
                break
            else:
                moves.append(Move((r, c), (row, c), self.board))
                row -= 1
        row = r + 1
        while row <= 7:
            if self.board[row][c][0] == turn:
                break
            elif self.board[row][c][0] != '-':
                moves.append(Move((r, c), (row, c), self.board))
                break
            else:
                moves.append(Move((r, c), (row, c), self.board))
                row += 1
        col = c - 1
        while col >= 0:
            if self.board[r][col][0] == turn:
                break
            elif self.board[r][col][0] != '-':
                moves.append(Move((r, c), (r, col), self.board))
                break
            else:
                moves.append(Move((r, c), (r, col), self.board))
                col -= 1
        col = c + 1
        while col <= 7:
            if self.board[r][col][0] == turn:
                break
            elif self.board[r][col][0] != '-':
                moves.append(Move((r, c), (r, col), self.board))
                break
            else:
                moves.append(Move((r, c), (r, col), self.board))
                col += 1
        return moves

    def getKnightMoves(self, r, c, moves):
        moves.extend([Move((r, c), (i, j), self.board) for i in range(8) for j in range(8)
                      if ((abs(r - i) == 1 and abs(c - j) == 2) or (abs(r - i) == 2 and abs(c - j) == 1)) and
                      self.board[i][j][0] != self.board[r][c][0]])
        return moves

    def getBishopMoves(self, r, c, moves):
        turn = self.board[r][c][0]
        row = r - 1
        col = c - 1
        while row >= 0 and col >= 0:
            sign = self.board[row][col][0]
            if sign == turn:
                break
            elif sign != '-':
                moves.append(Move((r, c), (row, col), self.board))
                break
            else:
                moves.append(Move((r, c), (row, col), self.board))
                row -= 1
                col -= 1
        row = r + 1
        col = c - 1
        while (row <= 7) and (col >= 0):
            sign = self.board[row][col][0]
            if sign == turn:
                break
            elif sign != '-':
                moves.append(Move((r, c), (row, col), self.board))
                break
            else:
                moves.append(Move((r, c), (row, col), self.board))
                row += 1
                col -= 1
        row = r - 1
        col = c + 1
        while (row >= 0) and (col <= 7):
            sign = self.board[row][col][0]
            if sign == turn:
                break
            elif sign != '-':
                moves.append(Move((r, c), (row, col), self.board))
                break
            else:
                moves.append(Move((r, c), (row, col), self.board))
                row -= 1
                col += 1
        row = r + 1
        col = c + 1
        while (row <= 7) and (col <= 7):
            sign = self.board[row][col][0]
            if sign == turn:
                break
            elif sign != '-':
                moves.append(Move((r, c), (row, col), self.board))
                break
            else:
                moves.append(Move((r, c), (row, col), self.board))
                row += 1
                col += 1
        return moves

    def getPawnMoves(self, r, c, moves):
        turn = self.board[r][c][0]
        if turn == "w":
            if self.board[r - 1][c] == '--':
                moves.append(Move((r, c), (r - 1, c), self.board))
            if r == 6 and self.board[r - 2][c] == '--':
                moves.append(Move((r, c), (r - 2, c), self.board))
            """
            capture to the right
            """
            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] not in [turn, '-']:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True))
            """
            capture to the left
            """
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] not in [turn, '-']:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True))
        else:
            if self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
            if r == 1 and self.board[r + 2][c] == '--':
                moves.append(Move((r, c), (r + 2, c), self.board))
            """
            capture to the right
            """
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] not in [turn, '-']:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True))
            """
            capture to the left
            """
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] not in [turn, '-']:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True))
        return moves

    def updateKingPosition(self):
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                if self.board[r][c] == 'wK':
                    self.whiteKingPosition = (r, c)
                elif self.board[r][c] == 'bK':
                    self.blackKingPosition = (r, c)


class CastlingRights:
    def __init__(self, wqs, wks, bqs, bks):
        self.wqs = wqs
        self.wks = wks
        self.bqs = bqs
        self.bks = bks


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or \
                               (self.pieceMoved == 'bp' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCastling = self.pieceMoved[1] == 'K' and abs(self.endCol - self.startCol) == 2
        self.promotionChoice = ['Q', 'R', 'N', 'B']
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    overriding the equals method
    """
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False  # if the other object is not even a "Move" it will always be False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    @property
    def end(self):
        return self.endRow, self.endCol

    @property
    def move(self):
        log = ''
        if self.pieceMoved[1] != 'p':
            log += self.pieceMoved[1]
        log += self.getRankFile(self.endRow, self.endCol)
        if self.pieceCaptured != '--':
            return log + '+'
        else:
            return log


if __name__ == '__main__':
    chess_board = ChessBoard()

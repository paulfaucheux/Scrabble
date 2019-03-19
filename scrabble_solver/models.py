from django.db import models

# Create your models here.
class Game(models.Model):
    scrabble_board          = models.
    scrabble_constraints    = models.

    def save(self, *args, **kwargs):
        self.scrabble_board = self.create_scrabble_board()
        self.scrabble_constraints = self.create_scrabble_constraints()
        return super(Scrabble, self).save(*args, **kwargs)
    
    def create_scrabble_board(self, *args, **kwargs):
        scrabble_board = np.zeros((11,11),dtype=object)
        for i in range(0,11):
            for j in range(0,11):
                scrabble_board[i,j] = '-'

        scrabble_board[0,2] = MOT_TRIPLE
        scrabble_board[0,8] = MOT_TRIPLE
        scrabble_board[2,4] = LETTRE_DOUBLE
        scrabble_board[2,6] = LETTRE_DOUBLE
        scrabble_board[1,5] = MOT_DOUBLE
        scrabble_board[3,7] = LETTRE_TRIPLE
        scrabble_board[2,8] = LETTRE_TRIPLE
        scrabble_board[1,9] = MOT_DOUBLE
        scrabble_board[0,10] = LETTRE_TRIPLE
        scrabble_board[2,10] = MOT_TRIPLE
        scrabble_board[4,8] = LETTRE_DOUBLE
        scrabble_board[5,9] = MOT_DOUBLE
        scrabble_board[6,8] = LETTRE_DOUBLE
        scrabble_board[8,10] = MOT_TRIPLE
        scrabble_board[0,0] = LETTRE_TRIPLE
        scrabble_board[1,1] = MOT_DOUBLE
        scrabble_board[2,2] = LETTRE_TRIPLE
        scrabble_board[3,3] = LETTRE_TRIPLE
        scrabble_board[7,7] = LETTRE_TRIPLE
        scrabble_board[8,8] = LETTRE_TRIPLE
        scrabble_board[9,9] = MOT_DOUBLE
        scrabble_board[10,10] = LETTRE_TRIPLE

        for i in range(0,scrabble_board.shape[0]):
            for j in range(0,i):
                scrabble_board[i,j] = scrabble_board[j,i]

        return scrabble_board

    def create_scrabble_constraints(self, *args, **kwargs):
        scrabble_constraints = np.zeros((11,11),dtype=object)
        for i in range(0,11):
            for j in range(0,11):
                scrabble_constraints[i,j] = '.'
        for i in range(0,scrabble_constraints.shape[0]):
            for j in range(0,i):
                scrabble_constraints[i,j] = scrabble_constraints[j,i]
        return scrabble_constraints
    
    def __str__(self):
        print('board')
        for i in range(0,11):
            print(' '.join([str(self.scrabble_board[i][j]) for j in range(0,11)]))

    def print_board(self):
        print('board')
        for i in range(0,11):
            print(' '.join([str(self.scrabble_board[i][j]) for j in range(0,11)]))

    def print_constraints(self):
        print('constraints: ')
        for i in range(0,11):
            print(' '.join([str(self.scrabble_constraints[i][j]) for j in range(0,11)]))

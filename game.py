import pygame,sys,os
pygame.init()
import random
from glob import glob



WHITE = (255,) * 3
BLACK = (0,) * 3
PURPLE = (255,0,255)
BGCOLOR = (170,190,255)
FPS = 60


SQUARE_SIZE = 64

class Menu:


    def __init__(self,screen_height,screen_width):
        
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.screen = pygame.display.set_mode((screen_width,screen_height))
        pygame.display.set_caption("BEJEWELED")

        Game(self.screen)






class Game:
    

    #IMAGES = [pygame.image.load(os.path.join('assets',file)).convert_alpha() for file in os.listdir('assets') if file.endswith('png')]
    TOP_PADDING = 50
    SIDE_PADDING = 100
    SQUARE_SIZE = 64
    INVALID_SWAP_SOUND = pygame.mixer.Sound(os.path.join('assets','badswap.wav'))
    SWAP_SOUNDS = [pygame.mixer.Sound(file) for file in glob('assets/match?.wav')]


    def __init__(self,screen,rows=8,cols=8):

        self.rows = rows
        self.cols = cols
        self.square_size = 64
        self.board_width = self.square_size * self.cols
        self.board_height = self.square_size * self.rows
        self.clock = pygame.time.Clock()
        self.selected = set()
        

        self.images = [pygame.image.load(os.path.join('assets',file)).convert_alpha() for file in os.listdir('assets') if file.endswith('png')]
        self.screen = screen
        self._initialize_board()
        self._play()
    
    
    @property
    def screen_height(self):
        return self.screen.get_height()

    @property
    def screen_width(self):
        return self.screen.get_width()

    def _initialize_board(self):

        
        self.top_padding = (self.screen_height - self.square_size * self.rows)//2
        self.side_padding = (self.screen_width - self.square_size * self.cols)//2
        self.board = []
        for row in range(self.rows):
            row = []
            for col in range(self.cols):
                row.append(random.choice(self.images))
            
            self.board.append(row)
    

    def _draw_board(self):


        for y in range(self.rows + 1):
            pygame.draw.line(self.screen,BLACK,(self.side_padding,self.top_padding + self.square_size * y),(self.side_padding + self.square_size * self.cols,self.top_padding + self.square_size * y))

        for x in range(self.cols + 1):
            pygame.draw.line(self.screen,BLACK,(self.side_padding + x * self.square_size,self.top_padding),(self.side_padding + x * self.square_size,self.top_padding + self.square_size * self.rows))

        
        
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col]:
                    self.screen.blit(self.board[row][col],(self.side_padding + col * self.square_size,self.top_padding + row * self.square_size))


        for row,col in self.selected:
            x = self.side_padding + self.square_size * col
            y = self.top_padding + self.square_size * row
            pygame.draw.rect(self.screen,PURPLE,(x,y,self.square_size,self.square_size),2)
    

    def _is_neighbor_cell(self,row_1,col_1,row_2,col_2):


        return abs(row_1 - row_2) <= 1 and abs(col_1 - col_2) <= 1




    
    def _swapAnimation(self,row_1,col_1,row_2,col_2):

        x1,y1 = self._get_x_and_y_from_row_col(row_1,col_1)
        x2,y2 = self._get_x_and_y_from_row_col(row_2,col_2)

        image_1 = self.board[row_1][col_1]
        image_2 = self.board[row_2][col_2]


        _image_2 = image_2
        _image_1 = image_1



        self.board[row_1][col_1] = self.board[row_2][col_2] = None
        
        horizontal= False
        if col_1 != col_2:
            horizontal = True
            if x1 > x2:
                x1,x2 = x2,x1
                image_1,image_2 = image_2,image_1
        else:
            if y1 > y2:
                y1,y2 = y2,y1
                image_1,image_2 = image_2,image_1

    

        while x1 <= x2 if horizontal else y1 <= y2:
            if horizontal:
                x1 += 5
                x2 -= 5 
            else:
                y1 += 5
                y2 -= 5
            self.screen.fill(BGCOLOR)
            self._draw_board()
            self.screen.blit(image_1,(x1,y1))
            self.screen.blit(image_2,(x2,y2))
            pygame.display.update()
            self.clock.tick(FPS)

        self.board[row_1][col_1] = _image_2
        self.board[row_2][col_2] = _image_1







    
    def _get_x_and_y_from_row_col(self,row,col):


        x = self.side_padding + col * self.square_size
        y = self.top_padding + row * self.square_size

        return x,y





    
    def _swapIfPossible(self):

        
        square_1,square_2 = self.selected

        row_1,col_1 = square_1
        row_2,col_2 = square_2
        

        if self._is_neighbor_cell(row_1,col_1,row_2,col_2) and self.board[row_1][col_1] is not self.board[row_2][col_2]:
            random.choice(self.SWAP_SOUNDS).play()
            self._swapAnimation(row_1,col_1,row_2,col_2)
        else:
            self.INVALID_SWAP_SOUND.play()


        self.selected.clear()

        return (row_1,col_1),(row_2,col_2)







    
    def _get_row_and_col(self,x,y):
        return (y - self.top_padding)//self.square_size,(x - self.side_padding)//self.square_size
    

    def _highlight_square(self,x,y):

        
        in_bounds = lambda x,y: self.side_padding < x < self.side_padding + self.board_width and self.top_padding < y < self.top_padding + self.board_height
        get_row_and_col = lambda x,y:  ((y - self.top_padding)//self.square_size,(x - self.side_padding)//self.square_size)


        if in_bounds(x,y):
            row,col = get_row_and_col(x,y)
            self.selected.add((row,col))





    

    def _check_direction(self,square,direction_delta):

        row_diff,col_diff = direction_delta

        row,col = square
        
        is_valid = False

        image = self.board[row][col]

        count = 1

        current_row,current_col = row + row_diff,col + col_diff

        in_bounds = lambda x,y: (0 <= current_row < len(self.board)) and (0 <= current_col < len(self.board[0]))
        



        while in_bounds(current_row,current_col) and self.board[current_row][current_col] is image:
            count += 1
            current_row += row_diff
            current_col += col_diff



        if count >= 3:
            row_diff *= -1
            col_diff *= -1
            current_row += row_diff
            current_col += col_diff
            while in_bounds(current_row,current_col) and self.board[current_row][current_col] is image:
                self.board[current_row][current_col] = None
                current_row += row_diff
                current_col += col_diff


            is_valid = True


        return is_valid










    def _checkForThreeInARow(self,square_1,square_2) -> bool:

        direction_deltas = [(0,1),(1,0),(-1,0),(0,-1)]
        

        # do temp swap
        row_1,col_1 = square_1 
        row_2,col_2 = square_2
        self.board[row_1][col_1],self.board[row_2][col_2] = self.board[row_2][col_2],self.board[row_1][col_1]
        is_valid = False
        for square in (square_1,square_2):
            row,col = square
            if self.board[row][col]:
                square_valid = False
                for direction_delta in direction_deltas:
                    square_valid = square_valid or self._check_direction(square,direction_delta)

                is_valid = is_valid or square_valid


                if square_valid:
                    row,col = square
                    self.board[row][col] = None


        
        if not is_valid:
            # swap back
            self.board[row_1][col_1],self.board[row_2][col_2] = self.board[row_2][col_2],self.board[row_1][col_1]
            self.INVALID_SWAP_SOUND.play()
        else:
            random.choice(self.SWAP_SOUNDS).play()


        return is_valid


    def _play(self):


        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x,y = pygame.mouse.get_pos()
                    self._highlight_square(x,y)
                    if len(self.selected) == 2:
                        square_1,square_2 = self.selected

                        self._checkForThreeInARow(square_1,square_2)

                        self.selected.clear()



            self.screen.fill(BGCOLOR)
            self._draw_board()
            pygame.display.update()




if __name__ == "__main__":
    height,width = 600,1000
    Menu(height,width)






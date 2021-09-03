import pygame,sys,os
import random



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

    
    def _swapAnimation(self,row_1,col_1,row_2,col_2):


        x1,y1 = self._get_x_and_y_from_row_col(row_1,col_1)
        x2,y2 = self._get_x_and_y_from_row_col(row_2,col_2)

        image_1 = self.board[row_1][col_1]
        image_2 = self.board[row_2][col_2]



        self.board[row_1][col_1] = self.board[row_2][col_2] = None


        while x1 <= x2:
            x1 += 5
            x2 -= 5 
            self.screen.fill(BGCOLOR)
            self._draw_board()
            self.screen.blit(image_1,(x1,y1))
            self.screen.blit(image_2,(x2,y2))
            pygame.display.update()
            self.clock.tick(FPS)

        self.board[row_1][col_1] = image_2
        self.board[row_2][col_2] = image_1







    
    def _get_x_and_y_from_row_col(self,row,col):


        x = self.side_padding + col * self.square_size
        y = self.top_padding + row * self.square_size

        return x,y





    
    def _swapIfPossible(self):

        square_1,square_2 = self.selected

        row_1,col_1 = square_1
        row_2,col_2 = square_2
        

        if self.board[row_1][col_1] is not self.board[row_2][col_2]:
            self._swapAnimation(row_1,col_1,row_2,col_2)


        self.selected.clear()







    
    def _get_row_and_col(self,x,y):
        return (y - self.top_padding)//self.square_size,(x - self.side_padding)//self.square_size
    

    def _highlight_square(self,x,y):

        
        in_bounds = lambda x,y: self.side_padding < x < self.side_padding + self.board_width and self.top_padding < y < self.top_padding + self.board_height
        get_row_and_col = lambda x,y:  ((y - self.top_padding)//self.square_size,(x - self.side_padding)//self.square_size)


        if in_bounds(x,y):
            row,col = get_row_and_col(x,y)
            self.selected.add((row,col))















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
                        self._swapIfPossible()



            
            self.screen.fill(BGCOLOR)
            self._draw_board()
            pygame.display.update()




if __name__ == "__main__":
    height,width = 600,1000
    Menu(height,width)






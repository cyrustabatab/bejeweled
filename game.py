import pygame,sys,os
import pprint as pp
pygame.init()
import random
import time
from glob import glob
from collections import defaultdict

# for each col find streak of consecutive pieces 
# start from max row to clear form each col and progress upwards
# tonight add timer action mode
# on new pieces dropped, create parallel matrix showing where pieces have been removed and just check each square for three in a row areas

WHITE = (255,) * 3
BLACK = (0,) * 3
PURPLE = (255,0,255)
BGCOLOR = (170,190,255)
RED = (255,0,0)
GREEN = (0,255,0)
FPS = 60

SQUARE_SIZE = 64

class Menu:


    def __init__(self,screen_height,screen_width):
        
        self.screen_height = screen_height
        self.screen_width = screen_width
        self.screen = pygame.display.set_mode((screen_width,screen_height))
        pygame.display.set_caption("BEJEWELED")

        Game(self.screen)



class Timer(pygame.sprite.Sprite):


    def __init__(self,x,y,width,height,seconds=10):
        super().__init__()

        self.image = pygame.Surface((width,height))
        self.image.fill(RED)
        self.seconds = self.total_seconds = seconds



        self.rect = self.image.get_rect(topleft=(x,y))
    

    def update(self):

        self.seconds -= 1
    

    def at_zero(self):
        return self.seconds == 0

    def increase_time(self):
        self.seconds += 3
        self.seconds = min(self.seconds,self.total_seconds)
    def draw(self,screen):

        screen.blit(self.image,self.rect)
        pygame.draw.rect(screen,GREEN,(*self.rect.topleft,(self.seconds/self.total_seconds) * self.rect.width,self.rect.height))


class Square(pygame.sprite.Sprite):


    def __init__(self,x,y,image):
        super().__init__()

        self.image = image
        self.rect = self.image.get_rect(topleft=(x,y))
        self.moving = False
    

    def update(self):
        if self.moving:
            if self.rect.y < self.target_y:
                self.rect.y += 5
            else:
                self.rect.y = self.target_y
                self.moving = False

    
    def set_target_diff(self,y_diff):

        self.target_y = self.rect.y + y_diff
        self.moving = True






    
    def _set_target_y(self,squares_removed, square_size):
        self.target_y = self.rect.y + square_size * squares_removed
        self.moving = True


    
    def equals(self,square):
        if isinstance(square,Square):
            return square.image is self.image


GEM_TO_SHAPE = {'gem1': 'P','gem2': 'C','gem3': 'D','gem4': 'S','gem5': 'H','gem6': 'B','gem7': 'T'}

class Game:
    

    #IMAGES = [pygame.image.load(os.path.join('assets',file)).convert_alpha() for file in os.listdir('assets') if file.endswith('png')]
    TOP_PADDING = 50
    SIDE_PADDING = 100
    SQUARE_SIZE = 64
    INVALID_SWAP_SOUND = pygame.mixer.Sound(os.path.join('assets','badswap.wav'))
    SWAP_SOUNDS = [pygame.mixer.Sound(file) for file in glob('assets/match?.wav')]
    SCORE_FONT = pygame.font.SysFont("calibri",25,bold=True)
    SCORE_FONT_BIG = pygame.font.SysFont("calibri",50,bold=True)


    def __init__(self,screen,rows=8,cols=8):

        self.rows = rows
        self.cols = cols
        self.square_size = 64
        self.board_width = self.square_size * self.cols
        self.board_height = self.square_size * self.rows
        self.clock = pygame.time.Clock()
        self.selected = set()
        self.score_texts = []
        self.hundred_text = self.SCORE_FONT.render("+100",True,GREEN)
        self.game_over = False
        self.game_over_surface = pygame.Surface((self.board_width,self.board_height),flags=pygame.SRCALPHA)
        self.game_over_surface.fill((0,0,0,128))
        self.overall_score_text =  self.SCORE_FONT_BIG.render("0",True,BLACK)
        self.overall_score = 0





        
        
        #self.images = [pygame.image.load(os.path.join('assets',file)).convert_alpha() for file in os.listdir('assets') if file.endswith('png')]
        self.mapping = {pygame.image.load(os.path.join('assets',file)).convert_alpha(): file.split(".")[0] for file in os.listdir('assets') if file.endswith('png')}


        self.images = list(self.mapping.keys())

        self.screen = screen
        self._initialize_board_and_timer()

        self._play()
    
    
    @property
    def screen_height(self):
        return self.screen.get_height()

    @property
    def screen_width(self):
        return self.screen.get_width()

    def _initialize_board_and_timer(self):

        
        self.top_padding = (self.screen_height - self.square_size * self.rows)//2
        self.side_padding = (self.screen_width - self.square_size * self.cols)//2
        self.squares = pygame.sprite.Group()
        self.board = []
        for row in range(self.rows):
            new_row = []
            for col in range(self.cols):
                # check two cols to left 
                removed_images = []
                if col - 2 >= 0 and new_row[col -1].image is new_row[col -2].image:
                    removed_images.append(new_row[col -1].image)
                    self.images.remove(new_row[col -1].image)

                if row - 2 >= 0 and self.board[row -1][col].image is self.board[row -2][col].image:
                    image = self.board[row -1][col].image
                    if image not in removed_images:
                        removed_images.append(image)
                        self.images.remove(removed_images[-1])
                image = random.choice(self.images)
                square = Square(*self._get_x_and_y_from_row_col(row,col),image)
                new_row.append(square)
                self.squares.add(square)

                for image in removed_images:
                    self.images.append(image)
            
            self.board.append(new_row)
        
        
        self.timer = pygame.sprite.GroupSingle(Timer(self.side_padding,self.top_padding + self.board_height,self.board_width,self.top_padding))


        self.board[0][0].image = self.images[0]
        self.board[0][1].image = self.images[1]
        self.board[0][2].image = self.images[1]
        self.board[1][0].image = self.images[1]
        self.board[1][1].image = self.images[0]
        self.board[1][2].image = self.images[0]
        self.board[1][3].image = self.images[0]
    

    def _draw_board(self):


        for y in range(self.rows + 1):
            pygame.draw.line(self.screen,BLACK,(self.side_padding,self.top_padding + self.square_size * y),(self.side_padding + self.square_size * self.cols,self.top_padding + self.square_size * y))

        for x in range(self.cols + 1):
            pygame.draw.line(self.screen,BLACK,(self.side_padding + x * self.square_size,self.top_padding),(self.side_padding + x * self.square_size,self.top_padding + self.square_size * self.rows))

        
        ''' 
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col]:
                    self.screen.blit(self.board[row][col],(self.side_padding + col * self.square_size,self.top_padding + row * self.square_size))
        '''
        self.squares.draw(self.screen)

        for row,col in self.selected:
            x = self.side_padding + self.square_size * col
            y = self.top_padding + self.square_size * row
            pygame.draw.rect(self.screen,PURPLE,(x,y,self.square_size,self.square_size),2)


        self.timer.sprite.draw(self.screen)
    

    def _is_neighbor_cell(self,row_1,col_1,row_2,col_2):


        return abs(row_1 - row_2) <= 1 and abs(col_1 - col_2) <= 1




    
    def _swapAnimation(self,row_1,col_1,row_2,col_2):

        x1,y1 = self._get_x_and_y_from_row_col(row_1,col_1)
        x2,y2 = self._get_x_and_y_from_row_col(row_2,col_2)

        image_1 = self.board[row_1][col_1].image
        image_2 = self.board[row_2][col_2].image


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





    

    def _check_direction(self,square,direction_delta,other_square):
        


        

        row_diff,col_diff = direction_delta
        row,col = square
        other_row,other_col = other_square
        is_valid = False
        image = self.board[row][col].image
        square_ = self.board[row][col]

        count = 1

        current_row,current_col = row + row_diff,col + col_diff




        in_bounds = lambda x,y: (0 <= current_row < len(self.board)) and (0 <= current_col < len(self.board[0]))
        
        
        


        
        start_end = []

        
        for i in range(2):
            while in_bounds(current_row,current_col) and self.board[current_row][current_col] and self.board[current_row][current_col].image is image:
                count += 1
                current_row += row_diff
                current_col += col_diff
            
            cell = (current_row - row_diff,current_col + row_diff)
            
            if i == 0:
                row_diff *= -1
                col_diff *= -1

                current_row = row + row_diff
                current_col = col + col_diff

        if count >= 3:
            row_diff *= -1
            col_diff *= -1
            current_row += row_diff
            current_col += col_diff
            start_end.append((current_row,current_col))
            while in_bounds(current_row,current_col) and self.board[current_row][current_col].image is image:
                square = self.board[current_row][current_col]
                self.board[current_row][current_col] = None
                square.kill()
                current_row += row_diff
                current_col += col_diff

            start_end.append((current_row - row_diff,current_col - col_diff))
            is_valid = True
            self.board[row][col] = square_


        return is_valid,start_end if start_end else None





    def _swapLocations(self,square_1,square_2):
        square_1.rect,square_2.rect = square_2.rect,square_1.rect




    def _checkForThreeInARow(self,square_1,square_2=None,on_move=True) -> bool:

        direction_deltas = [(0,1),(1,0)]
        

        # do temp swap
        if on_move:
            row_1,col_1 = square_1 
            row_2,col_2 = square_2


            if self.board[row_1][col_1].equals(self.board[row_2][col_2]):
                return 
            
            self._swapLocations(self.board[row_1][col_1],self.board[row_2][col_2])
            self.board[row_1][col_1],self.board[row_2][col_2] = self.board[row_2][col_2],self.board[row_1][col_1]
            is_valid = False
            previous_count = None
            start_ends = []
            
            print(square_1,square_2)
        for square in (square_1,square_2):
            row,col = square
            other_square = square_2 if square is square_1 else square_1
            if self.board[row][col]:
                square_valid = False
                for direction_delta in direction_deltas:
                    valid_direction,start_end = self._check_direction(square,direction_delta,other_square)
                    if start_end:
                        start_ends.append(start_end)


                    square_valid = square_valid or valid_direction

                is_valid = is_valid or square_valid

            '''
            if row_1 == row_2:
                direction_deltas.pop(0)
            else:
                direction_deltas.pop()
            '''
            if square_valid:
                self.board[row][col] = None # swap only after checking everything


        


        
        if not is_valid:
            # swap back
            self._swapLocations(self.board[row_1][col_1],self.board[row_2][col_2])
            self.board[row_1][col_1],self.board[row_2][col_2] = self.board[row_2][col_2],self.board[row_1][col_1]
            self.INVALID_SWAP_SOUND.play()
        else:
            random.choice(self.SWAP_SOUNDS).play()


        return start_ends
    

    def _dropAllPiecesMultipleColumns(self,min_row,max_row,col):
        
        _,goal_y = self._get_x_and_y_from_row_col(max_row,col) 


        current_coordinate = {}


        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            movement = False
            for r in reversed(range(0,min_row)): 
                for col in range(min_col,max_col + 1):
                    current_x,current_y = self._get_x_and_y_from_row_col(r,col)
                    
                    if (r,col) not in current_coordinate:
                        current_coordinate[(r,col)] = [current_x,current_y,self.board[r][col]]
                        self.board[r][col] = None
                    if current_coordinate[(r,col)][1] < goal_y:
                        current_coordinate[(r,col)][1] += 2
                        movement = True
                    
                    x,y,image = current_coordinate[(r,col)]
                    self.screen.blit(image,(x,y))
            if not movement:
                return
            
            self.screen.fill(BGCOLOR)
            self._draw_board()
            pygame.display.update()
            self.clock.tick(FPS)
    

    def _dropAColumn(self,min_row,max_row,col):
        '''
            col = square_1[1]
            min_row = min(square_1[0],square_2[0])
            max_row = max(square_1[0],square_2[0])
        '''

        squares_cleared = max_row - min_row + 1
        x,_ = self._get_x_and_y_from_row_col(max_row,col) 

            
            
        squares_to_add = (max_row + 1) - (min_row)
    
        current_row = max_row
        for row in reversed(range(0,min_row)):
            self.board[row][col].set_target_diff(squares_cleared * self.square_size)
            self.board[current_row][col] = self.board[row][col]
            current_row -= 1

        if squares_to_add > 0:

            for i in range(squares_to_add):
                square = Square(x,(self.top_padding) - 64 * (i + 1),random.choice(self.images))
                square.set_target_diff(squares_to_add * self.square_size)
                self.board[squares_to_add -1 - i][col] = square
                self.squares.add(square)



    def _dropAndInsertNewPieces(self,start_ends):
        
        

        start_ends.sort()
        
        check_squares_range = []

        for start_end in start_ends:
            square_1,square_2 = start_end
            if square_1[0] == square_2[0]:
               col_1,col_2  = square_1[1],square_2[1]
               min_col = min(col_1,col_2)
               max_col = max(col_1,col_2)
               row = square_1[0]
               for col in range(min_col,max_col + 1):
                   check_squares_range.append(((col,0),(col,row)))
                   self._dropAColumn(row,row,col)

            else:
                col = square_1[1]
                min_row = min(square_1[0],square_2[0])
                max_row = max(square_1[0],square_2[0])
                check_squares_range.append(((col,0),(col,max_row)))
                self._dropAColumn(min_row,max_row,col)
                '''
                squares_cleared = max_row - min_row + 1

                x,_ = self._get_x_and_y_from_row_col(max_row,col) 

                
                
                squares_to_add = (max_row + 1) - (min_row)
                print(squares_cleared,min_row)
                print(squares_to_add)
            
                current_row = max_row
                for row in reversed(range(0,min_row)):
                    self.board[row][col].set_target_diff(squares_cleared * self.square_size)
                    self.board[current_row][col] = self.board[row][col]
                    current_row -= 1

                if squares_to_add > 0:

                    for i in range(squares_to_add):
                        square = Square(x,(self.top_padding) - 64 * (i + 1),random.choice(self.images))
                        square.set_target_diff(squares_to_add * self.square_size)
                        self.board[squares_to_add -1 - i][col] = square
                        self.squares.add(square)



                


               # self._dropAndInsertNewPieces(max_row,min_row,col)
               '''

    
    def _get_middle_between_two_squares(self,start_ends):








        for start_end in start_ends:
            square_1,square_2 = start_end


            if square_1[0] == square_2[0]:


                row = square_1[0]
                min_value = min(square_1[1],square_2[1])
                max_value = max(square_1[1],square_2[1])
                squares = max_value - min_value + 1

                score = 100 + 20 * (squares - 3)
                self.overall_score += score
                self.overall_score_text = self.SCORE_FONT_BIG.render(f"{self.overall_score}",True,BLACK)




                score_text = self.SCORE_FONT.render(f"+{score}",True,GREEN)


                min_x,min_y = self._get_x_and_y_from_row_col(row,min_value)
                max_x,max_y = self._get_x_and_y_from_row_col(row,max_value)

                value=  min_x + (max_x + self.square_size - min_x)//2 - self.hundred_text.get_width()//2,min_y + self.square_size//2 - self.hundred_text.get_height()//2
                self.score_texts.append((score_text,value))
            else:
                col = square_1[1]

                min_value = min(square_1[0],square_2[0])
                max_value = max(square_1[0],square_2[0])


                squares = max_value - min_value + 1

                score = 100 + 20 * (squares - 3)


                score_text = self.SCORE_FONT.render(f"+{score}",True,GREEN)

                min_x,min_y = self._get_x_and_y_from_row_col(min_value,col)
                max_x,max_y = self._get_x_and_y_from_row_col(max_value,col)

                value = min_x + self.square_size//2 - self.hundred_text.get_width()//2,min_y +(max_y - min_y)//2 - self.hundred_text.get_height()//2
                self.score_texts.append((score_text,value))



    

    def _get_true_start_ends(self,start_ends):

        col_to_max_row =defaultdict(int)

        for square_1,square_2 in start_ends:
            row_1,col_1 = square_1
            row_2,col_2 = square_2

            if row_1 == row_2:
                min_col = min(col_1,col_2)
                max_col = max(col_1,col_2)
                for col in range(min_col,max_col + 1):
                    col_to_max_row[col] = max(col_to_max_row[col],row_1)
            else:
                max_row = max(row_1,row_2)
                col_to_max_row[col_1] = max(col_to_max_row[col_1],max_row)

    

    def print_board(self):


        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col]:
                    print(GEM_TO_SHAPE[self.mapping[self.board[row][col].image]],end=' ')
                else:
                    print(0,end=' ')

            print()
    
    def _dropAndInsertNewPieces2(self,start_ends):


        print(start_ends)      
        row_to_max_col = defaultdict(int)


        squares_with_new_gems = []

        for square_1,square_2 in start_ends:
            row_1,col_1 = square_1
            row_2,col_2 = square_2

        



            if col_1 == col_2:
                row_to_max_col[col_1] = max(row_1,row_2)
            else:

                min_col = min(col_1,col_2)
                max_col = max(col_1,col_2)



                for col in range(min_col,max_col + 1):
                    row_to_max_col[col] = max(row_to_max_col[col],row_1)
                    row_to_max_col[col] = max(row_to_max_col[col],row_2)

        

        print(row_to_max_col)


        for col,row in row_to_max_col.items():
            current_row = row
            

            removed = 0
            count = 0
            while current_row >= 0:
                count += 1
                if self.board[current_row][col] is not None:

                    self.board[current_row][col].set_target_diff(self.square_size *removed)
                    squares_with_new_gems.append((current_row + removed,col))
                    self.board[current_row + removed][col] = self.board[current_row][col]
                else:
                    removed += 1
                current_row -= 1


        

            x,_ = self._get_x_and_y_from_row_col(row,col)
            for i in range(removed):
                square = Square(x,self.top_padding - self.square_size * (i + 1),random.choice(self.images))
                square.set_target_diff(removed * self.square_size)
                squares_with_new_gems.append((removed -1 - i,col))
                self.board[removed -1 - i][col] = square
                self.squares.add(square)
            
        return squares_with_new_gems
    

    def _check_squares_with_new_gems(self):


        self.temp_board = [[1 for _ in range(len(self.board[0]))] for _ in range(len(self.board))]
    def _play(self):

        score_start_time = None

        TIME_EVENT = pygame.USEREVENT + 2
        pygame.time.set_timer(TIME_EVENT,1000)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if not self.game_over:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        x,y = pygame.mouse.get_pos()
                        self._highlight_square(x,y)
                        if len(self.selected) == 2:
                            square_1,square_2 = self.selected

                            start_ends = self._checkForThreeInARow(square_1,square_2)
                            if start_ends:
                                self.timer.sprite.increase_time()
                                print()
                                self.print_board()
                                self._get_middle_between_two_squares(start_ends)
                                score_start_time = time.time()
                                squares_with_new_gems = self._dropAndInsertNewPieces2(start_ends)

                                self._check_squares_with_new_gems()
                                print(squares_with_new_gems)
                                print()
                                self.print_board()

                            self.selected.clear()
                    elif event.type == TIME_EVENT:
                        self.timer.sprite.update()

            if score_start_time:
                current_time = time.time()
                if current_time - score_start_time >= 1:
                    score_start_time = None
                    self.score_texts = []
            
            if self.timer.sprite.at_zero():
                self.game_over = True
        
            if not self.game_over:
                self.squares.update()
            self.screen.fill(BGCOLOR)
            self._draw_board()
            if score_start_time:
                for score,coordinate in self.score_texts:
                    self.screen.blit(score,coordinate)
            if self.game_over:
                game_over_font = pygame.font.SysFont("calibri",60,bold=True)
                game_over_text = game_over_font.render("GAME OVER",True,RED)
                game_over_text_rect = game_over_text.get_rect(center=(self.screen_width//2,self.screen_height//2))
                self.screen.blit(self.game_over_surface,(self.side_padding,self.top_padding))
                self.screen.blit(game_over_text,game_over_text_rect)
            
            self.screen.blit(self.overall_score_text,(0,0))
            pygame.display.update()




height,width = 600,1000
Menu(height,width)






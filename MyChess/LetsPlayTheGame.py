from ChessBoard import *

b = Board(game_mode_classic)
print(b, 'Start of the Game')
no_checkmate = True
white = b.player_white
black = b.player_black

while no_checkmate:
    player = {0: white, 1: black}[b.turn % 2]
    b.look_for_cells_are_attacked()
    b.move_creator()
    print('If someone in check:', bool(b.someone_in_check))
    player.print_possible_moves()
    if len(player.possible_moves) == 0:
        no_checkmate = False
        print(f'{ {1: white, 0: black}[b.turn % 2] } won the Game, congratulations!')
        continue
    print(f'{player.color} to move')
    print(b.encryption_forsyth_edwards())
    offered_move = input().split()
    while offered_move not in player.possible_moves:
        print(f'{ offered_move } is not available move, try again:')
        offered_move = input().split()
    b.move(offered_move)
    print(b)




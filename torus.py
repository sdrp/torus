#!/usr/bin/env python

# Torus Checkers
# Sudheesha Perera
# Spring 2016

#############################################################################

import sys
import math
import copy

#############################################################################
# Definitions for two helper classes, essentially just abstractions
class Move:
	def __init__(self, piece_to_move, board):
		self.moves_list = [piece_to_move]
		self.board = board 
		self.is_simple_move = True # create a simple move

class Board:
	def __init__(self, red_pieces, white_pieces):
		self.red_pieces = red_pieces
		self.white_pieces = white_pieces 

# A function to open the input file and parse its contents
def parse_file(board_filename):
	f = open(board_filename, 'r')
	first_line = f.readline()
	if first_line == "terminate":
		sys.exit()
	# (1)
	first_line = first_line.split() 
	if first_line[0] != 'g':
		print "Improper File Input"
		#sys.exit()
	else:
		board_dim = int(first_line[1])
		max_turns = int(first_line[3])
	# (2)
	second_line = f.readline().split()
	if second_line[0] != 'p':
		print "Improper File Input"
		#sys.exit()
	else:
		turns_so_far = int(second_line[1])
		if int(second_line[2]):
			player_to_move = 'white'
		else:
			player_to_move = 'red'
	# (3)
	third_line = f.readline().split()
	if third_line[0] != 'r':
		print "Improper File Input"
		#sys.exit()
	else:
		num_red = int(third_line[1])
		red_pos = [int(x) for x in third_line[2:]]
	# (4)
	fourth_line = f.readline().split()
	if fourth_line[0] != 'w':
		print "Improper File Input"
		#sys.exit()
	else:
		num_white = int(fourth_line[1])
		white_pos = [int(x) for x in fourth_line[2:]]

	f.close()
	board = Board(red_pos, white_pos)
	return (board_dim, max_turns, turns_so_far, player_to_move, board)

# A function to print a Board object
def print_board(board):
	blank_square = '[_]'
	for row in range(0, 8):
		row_str = ''
		odd_row = row % 2 # a boolean 
		for col in range(1,9):
			squ_num = (8*row) + col
			if ((squ_num % 2) == 0) ^ odd_row:  # logical xor
				loc_num = math.ceil(float(squ_num) / 2)
				if loc_num in board.red_pieces:
					row_str += '[R]'
				elif loc_num in board.white_pieces:
					row_str += '[W]'
				else:
					row_str += blank_square
			else:
				row_str += blank_square
		print row_str

# A function to print a Move object
def print_move(move):
	board = move.board
	moves_list = move.moves_list
	final_pos = moves_list[-1]
	blank_square = '[_]'
	touched_square = '{-}'
	touch_val = 1

	if final_pos in board.red_pieces:
		final_square = "{R}"
	elif final_pos in board.white_pieces:
		final_square = "{W}"
	else:
		print "Error in print_move!"
		#sys.exit()
	for row in range(0, 8):
		row_str = ''
		odd_row = row % 2 # a boolean 
		for col in range(1,9):
			squ_num = (8*row) + col
			if ((squ_num % 2) == 0) ^ odd_row:  # logical xor
				loc_num = math.ceil(float(squ_num) / 2)
				if loc_num == final_pos:
					row_str += final_square
				elif loc_num in moves_list:
					row_str +=  ("{%s}" % str(touch_val))
					touch_val += 1
				elif loc_num in board.red_pieces:
					row_str += '[R]'
				elif loc_num in board.white_pieces:
					row_str += '[W]'
				else:
					row_str += blank_square
			else:
				row_str += blank_square
		print row_str

# A function to output result of move to a new file, with the player to
# move now switched to the opponent
def output_move_to_file(move, turns_so_far, player_to_move):
	f = open("temp_board", 'w')
	if move == None: # if execution should have terminated
		f.write("terminate")
		f.close()
	else:
		red_pieces = [str(piece) for piece in move.board.red_pieces]
		white_pieces = [str(piece) for piece in move.board.white_pieces]	
		f.write("g 8 8 100\n")
		second_line = "p %d %d\n" % (turns_so_far + 1, 1 if player_to_move == "red" else 0)
		third_line = "r " + str(len(move.board.red_pieces)) + " " + " ".join(red_pieces) + "\n"
		fourth_line = "w " + str(len(move.board.white_pieces)) + " " + " ".join(white_pieces) + "\n"
		f.write(second_line)
		f.write(third_line)
		f.write(fourth_line)
		f.close()

##############################################################################################
# A function to generate all legal moves for a given board and player color
# Calls on helper functions generate_moves_red and generate_moves_white, mirrors of each other
def all_legal_moves(board, color_to_play):
	# Returns a list of Move objects representing all legal moves
	# that can be make by the color to play
	all_moves = []
	if color_to_play == 'red':
		for piece in board.red_pieces:
			all_moves += generate_moves_red(piece, board)
	elif color_to_play == 'white':
		for piece in board.white_pieces:
			all_moves += generate_moves_white(piece, board)
	else:
		print "Invalid color_to_play input to all_legal_moves"
	# Now make sure that all simple moves are removed if 
	# capture moves are available
	capture_moves = [move for move in all_moves if (not move.is_simple_move)]
	if capture_moves == []: # There are no capture moves possible
		return all_moves
	else: # Return only the capture moves 
		return capture_moves

def generate_moves_red(piece_to_move, board):
	all_possible_moves = []
	
	def is_even_row(squ_val):
		return (squ_val % 8) in [1, 2, 3, 4]

	def diag_DR(squ_val):
		# Takes the square value and returns the square "down and right" of it
		if squ_val in [4, 12, 20, 28]:
			return squ_val + 1
		else:
			# Not in the last column, check if even or odd row
			if is_even_row(squ_val): # Even row
				return squ_val + 5
			else: # Odd row
				return (squ_val + 4) % 32 # mod 32 corrects for moves past the bottom edge

	def diag_DL(squ_val):
		# Returns square "down and left" of input
		if squ_val in [5, 13, 21]:
			return squ_val + 7
		elif squ_val == 29:
			return 4
		else:
			# Check if even or odd row
			if is_even_row(squ_val):
				return squ_val + 4
			else:
				return (squ_val + 3) % 32 # mod 32 corrects for moves past the bottom edge 

	def try_capture_recursive(piece_to_move, move_seed):
		# Called because a white piece is adjacent
		adj_space_DR = diag_DR(piece_to_move)
		double_adj_space_DR = diag_DR(adj_space_DR)
		adj_space_DL = diag_DL(piece_to_move)
		double_adj_space_DL = diag_DL(adj_space_DL)	
		
		# Three checks for jump operation DR
		check_1_DR = adj_space_DR in move_seed.board.white_pieces # there's a white piece to capture
		check_2_DR = double_adj_space_DR not in move_seed.board.red_pieces # no blocking red piece
		check_3_DR = double_adj_space_DR not in move_seed.board.white_pieces # no blocking white piece
		check_DR = check_1_DR and check_2_DR and check_3_DR

		# Three checks for jump operation DL
		check_1_DL = adj_space_DL in move_seed.board.white_pieces # there's a white piece to capture
		check_2_DL = double_adj_space_DL not in move_seed.board.red_pieces # no blocking red piece
		check_3_DL = double_adj_space_DL not in move_seed.board.white_pieces # no blocking white piece
		check_DL = check_1_DL and check_2_DL and check_3_DL

		if check_DR:
			# No piece in the way diagonal right...create a new capture move building on the seed
			new_capture_move = copy.deepcopy(move_seed)
			new_capture_move.is_simple_move = False
			new_capture_move.moves_list.append(double_adj_space_DR)
			new_capture_move.board.red_pieces.remove(piece_to_move)
			new_capture_move.board.red_pieces.append(double_adj_space_DR)
			new_capture_move.board.white_pieces.remove(adj_space_DR)
			# Call function recursively twice, looking for subsequent captures
			# Now the first argument, "piece to move" is the double adjacent space
			try_capture_recursive(double_adj_space_DR, copy.deepcopy(new_capture_move))
		
		if check_DL:
			# No piece in the way diagonal left...create a new capture move building on the seed
			new_capture_move = copy.deepcopy(move_seed)
			new_capture_move.is_simple_move = False
			new_capture_move.moves_list.append(double_adj_space_DL)
			new_capture_move.board.red_pieces.remove(piece_to_move)
			new_capture_move.board.red_pieces.append(double_adj_space_DL)
			new_capture_move.board.white_pieces.remove(adj_space_DL)
			# Call function recursively twice, looking for subsequent captures
			# Now the first argument, "piece to move" is the double adjacent space
			try_capture_recursive(double_adj_space_DL, copy.deepcopy(new_capture_move))				
		
		if (not check_DR) and (not check_DL):
			# There is a piece in the way.
			if len(move_seed.moves_list) > 1: 
				# Seed contains actual moves, not just original piece position
				all_possible_moves.append(move_seed)

	def try_simple(piece_to_move, direction, move_seed):
		# 1) Get the adjacent space
		if direction == 'DR':
			adj_space = diag_DR(piece_to_move)
		elif direction == 'DL':
			adj_space = diag_DL(piece_to_move)
		else:
			print "Invalid Direction for generate_moves_red"
			return None

		# 2) Check if a simple move can be made, otherwise call recursive helper
		if adj_space in move_seed.board.white_pieces:
			try_capture_recursive(piece_to_move, copy.deepcopy(move_seed))
		elif adj_space not in move_seed.board.red_pieces: # no red piece or white piece in the way
			new_simp_move = Move(piece_to_move, copy.deepcopy(move_seed.board))
			new_simp_move.moves_list.append(adj_space)
			new_simp_move.board.red_pieces.remove(piece_to_move)
			new_simp_move.board.red_pieces.append(adj_space)
			all_possible_moves.append(new_simp_move)

	move_seed = Move(piece_to_move, board) # The original board, no move made yet 
	try_simple(piece_to_move, 'DR', copy.deepcopy(move_seed))
	try_simple(piece_to_move, 'DL', copy.deepcopy(move_seed))

	return all_possible_moves

def generate_moves_white(piece_to_move, board):
	all_possible_moves = []
	
	def is_even_row(squ_val):
		return (squ_val % 8) in [1, 2, 3, 4]

	def diag_UR(squ_val):
		# Returns square "up and to the right" of input
		if squ_val in [12, 20, 28]:
			return squ_val - 7
		elif squ_val == 4:
			return 29
		else:
			if squ_val in [1, 2, 3]:
				return 32 + (squ_val - 3)
			elif is_even_row(squ_val):
				return squ_val - 3
			else:
				return squ_val - 4

	def diag_UL(squ_val):
		# Returns square "up and to the left" of input
		if squ_val in [1, 2, 3, 4]: # off the top edge
			return squ_val + 28
		elif squ_val in [5, 13, 21, 29]:
			return squ_val - 1
		else:
			if is_even_row(squ_val):
				return squ_val - 4
			else:
				return squ_val - 5

	def try_capture_recursive(piece_to_move, move_seed):
		# Called because a red piece is adjacent
		adj_space_UR = diag_UR(piece_to_move)
		double_adj_space_UR = diag_UR(adj_space_UR)
		adj_space_UL = diag_UL(piece_to_move)
		double_adj_space_UL = diag_UL(adj_space_UL)	
		
		# Three checks for jump operation UR
		check_1_UR = adj_space_UR in move_seed.board.red_pieces # there's a red piece to capture
		check_2_UR = double_adj_space_UR not in move_seed.board.red_pieces # no blocking red piece
		check_3_UR = double_adj_space_UR not in move_seed.board.white_pieces # no blocking white piece
		check_UR = check_1_UR and check_2_UR and check_3_UR

		# Three checks for jump operation UL
		check_1_UL = adj_space_UL in move_seed.board.red_pieces # there's a red piece to capture
		check_2_UL = double_adj_space_UL not in move_seed.board.red_pieces # no blocking red piece
		check_3_UL = double_adj_space_UL not in move_seed.board.white_pieces # no blocking white piece
		check_UL = check_1_UL and check_2_UL and check_3_UL

		if check_UR:
			# No piece in the way diagonal right...create a new capture move building on the seed
			new_capture_move = copy.deepcopy(move_seed)
			new_capture_move.is_simple_move = False
			new_capture_move.moves_list.append(double_adj_space_UR)
			new_capture_move.board.white_pieces.remove(piece_to_move)
			new_capture_move.board.white_pieces.append(double_adj_space_UR)
			new_capture_move.board.red_pieces.remove(adj_space_UR)
			# Call function recursively twice, looking for subsequent captures
			# Now the first argument, "piece to move" is the double adjacent space
			try_capture_recursive(double_adj_space_UR, copy.deepcopy(new_capture_move))
		
		if check_UL:
			# No piece in the way diagonal left...create a new capture move building on the seed
			new_capture_move = copy.deepcopy(move_seed)
			new_capture_move.is_simple_move = False
			new_capture_move.moves_list.append(double_adj_space_UL)
			new_capture_move.board.white_pieces.remove(piece_to_move)
			new_capture_move.board.white_pieces.append(double_adj_space_UL)
			new_capture_move.board.red_pieces.remove(adj_space_UL)
			# Call function recursively twice, looking for subsequent captures
			# Now the first argument, "piece to move" is the double adjacent space
			try_capture_recursive(double_adj_space_UL, copy.deepcopy(new_capture_move))				
		
		if (not check_UR) and (not check_UL):
			# There is a piece in the way.
			if len(move_seed.moves_list) > 1: 
				# Seed contains actual moves, not just original piece position
				all_possible_moves.append(move_seed)

	def try_simple(piece_to_move, direction, move_seed):
		# 1) Get the adjacent space
		if direction == 'UR':
			adj_space = diag_UR(piece_to_move)
		elif direction == 'UL':
			adj_space = diag_UL(piece_to_move)
		else:
			print "Invalid Direction for generate_moves_white"
			return None

		# 2) Check if a simple move can be made, otherwise call recursive helper
		if adj_space in move_seed.board.red_pieces:
			try_capture_recursive(piece_to_move, copy.deepcopy(move_seed))
		elif adj_space not in move_seed.board.white_pieces: # no red piece or white piece in the way
			new_simp_move = Move(piece_to_move, copy.deepcopy(move_seed.board))
			new_simp_move.moves_list.append(adj_space)
			new_simp_move.board.white_pieces.remove(piece_to_move)
			new_simp_move.board.white_pieces.append(adj_space)
			all_possible_moves.append(new_simp_move)

	move_seed = Move(piece_to_move, board) # The original board, no move made yet 
	try_simple(piece_to_move, 'UR', copy.deepcopy(move_seed))
	try_simple(piece_to_move, 'UL', copy.deepcopy(move_seed))

	return all_possible_moves

#######################################################################################
# The Static Evaluation Function
def static_eval_func_basic(board):
	return len(board.red_pieces) - len(board.white_pieces)

def weighted_refined(weights):
	# Weight the positions on the board, central locations more favorable
	# The weighted value addition never amounts to more than the value of a piece
	# Ie. the weights are only used to break ties that result in the "basic" function
	center = [15, 18]
	inner_ring = [10, 11, 14, 19, 22, 23]
	outer_ring = [6, 7, 8, 9, 16, 17, 24, 25, 26, 27]
	outer_loop = [1, 2, 3, 4, 5, 13, 21, 29, 30, 31, 32, 28, 20, 12]
	
	def weighting_func(x, weights):
		if x in center:
			return weights[0]
		elif x in inner_ring:
			return weights[1]
		elif x in outer_ring:
			return weights[2]
		elif x in outer_loop:
			return weights[3]

	def evaluation(weights, red_pieces, white_pieces):
		max_val = (max(weights) * 12) + 1
		red_val = float(sum([weighting_func(piece, weights) for piece in red_pieces])) / (2 * max_val)
		white_val = float(sum([weighting_func(piece, weights) for piece in white_pieces])) / (2 * max_val)
		return (len(red_pieces) - len(white_pieces)) + (red_val - white_val) 

	return lambda board: evaluation(weights, board.red_pieces, board.white_pieces)


#######################################################################################
# The Alpha-Beta Search Algorithm 
def minimax_alpha_beta(board, color_to_play, A, B, depth, static_eval_func):
	# A and B are the recursively passed boundary conditions
	# depth is how far we want the recursion to continue
	alpha = float("-inf")
	beta = float("inf")

	beta_move = None
	alpha_move = None

	possible_moves = all_legal_moves(board, color_to_play)
	if (possible_moves == []) or (depth == 0):
		# no move can be made, or we've reached the recursion limit
		return (static_eval_func(board), None) # tuple of (value, Move)

	if color_to_play == "white":
		# Node is a MIN node
		for move in possible_moves:
			(val, val_board) = minimax_alpha_beta(move.board, "red", A, min(B, beta), depth - 1, static_eval_func)
			if val < beta:
				beta = val
				beta_move = move
			if A >= beta:
				return (beta, beta_move) # The corresponding board is meaningless in this case
		return (beta, beta_move)

	if color_to_play == "red":
		# Node is a MAX node
		for move in possible_moves:
			(val, val_board) = minimax_alpha_beta(move.board, "white", max(alpha, A), B, depth - 1, static_eval_func)
			if val > alpha:
				alpha = val
				alpha_move = move
			if B <= alpha:
				return (alpha, alpha_move)
		return (alpha, alpha_move)

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
# BEGIN CHECKERS LOGIC #
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
def make_move(board_dim, max_turns, turns_so_far, player_to_move, board, static_eval_func, search_depth, print_str):
	# Create the template for the output line
	num_red = len(board.red_pieces)
	num_white = len(board.white_pieces)
	output_line = ["m", str(turns_so_far), "0" if player_to_move == "red" else "1"]
	print_bool = False if print_str == "PRINT_OFF_TOTAL" else True
	# Now go through each game case (win, loss, draw, or move to be made)
	# 1) Max Turn Limit has been reached, resulting in a draw
	if turns_so_far > max_turns:
		if num_red > num_white:
			if print_bool:
				if player_to_move == "white":
					print " ".join(output_line + ["0", "-1"])
				elif player_to_move == "red":
					print " ".join(output_line + ["0", "1"])
				print "RED WON!"
				print_board(board)
			output_move_to_file(None, None, None)
			return ("RED WON!", board.red_pieces, board.white_pieces)
		elif num_white > num_red:
			if print_bool:
				if player_to_move == "white":
					print " ".join(output_line + ["0", "1"])
				elif player_to_move == "red":
					print " ".join(output_line + ["0", "-1"])
				print "WHITE WON!"
				print_board(board)
			output_move_to_file(None, None, None)
			return ("WHITE WON!", board.red_pieces, board.white_pieces)
		else:
			if print_bool: 
				print " ".join(output_line + ["0", "0"])
				print "DRAW"
			return ("DRAW", board.red_pieces, board.white_pieces)
	# 2) Check if num_red or num_white is 0 (win for one of the sides)
	if num_white == 0:
		if print_bool:
			if player_to_move == "white":
				print " ".join(output_line + ["0", "-1"])
			elif player_to_move == "red":
				print " ".join(output_line + ["0", "1"])
			print "RED WON!"
			print_board(board)
		output_move_to_file(None, None, None)
		return ("RED WON!", board.red_pieces, board.white_pieces)
	if num_red == 0:
		if print_bool:
			if player_to_move == "red":
				print " ".join(output_line + ["0", "-1"])
			elif player_to_move == "white":
				print " ".join(output_line + ["0", "1"])
			print "WHITE WON!"
			print_board(board)
		output_move_to_file(None, None, None)
		return ("WHITE WON!", board.red_pieces, board.white_pieces)
	# 3) Check if no move can be make by the player to move 
	possible_moves = all_legal_moves(board, player_to_move)
	if possible_moves == []:
		if player_to_move == "red":
			other_player = "white"
		elif player_to_move == "white":
			other_player = "red"
		
		if print_bool:
			print " ".join(output_line + ["0", "-1"])
			print "%s WON!" % other_player.upper()
		return ("%s WON!" % other_player.upper(), board.red_pieces, board.white_pieces)
	# 4) The game hasn't ended - output the best possible move
	(val, move) = minimax_alpha_beta(board, player_to_move, float("-inf"), float("inf"), search_depth, static_eval_func)
	if print_bool:	
		output_line +=  [str(pos) for pos in move.moves_list] # Add the picked move squares
		print " ".join(output_line) # Print the move in correct format

	if print_str == "PRINT_ON":
		# Print the original board
		print "Player to Move: |%s|" % player_to_move.upper()
		print "The Move: " + str(move.moves_list) 
		print "Board After Move"
		print_move(move) # Print out the resulting board after move
		print ""
	output_move_to_file(move, turns_so_far, player_to_move)
	return ("MID_GAME", board.red_pieces, board.white_pieces) 

if __name__ == '__main__':
	# Parse the command line inputs
	cmd_ln = sys.argv
	if len(cmd_ln) != 2:
		print "Improper Number of Inputs" 
		print "Input Format: python torus_checkers.py board_filename"
		#sys.exit() # Exit the program
	board_filename = cmd_ln[1] 
	static_eval_fn = weighted_refined([0, 0, 1, 0])
	(board_dim, max_turns, turns_so_far, player_to_move, board) = parse_file(board_filename)
	make_move(board_dim, max_turns, turns_so_far, player_to_move, board, static_eval_fn, 3, "PRINT_ON")


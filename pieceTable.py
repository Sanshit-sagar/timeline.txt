from enum import Enum, auto 

class Piece: 
    def __init__(self, buf_type, buf_ind, piece_len): 
        self.buffer_type = buf_type
        self.buffer_start = buf_ind
        self.length = piece_len
    
    def __str__(self): 
        return f'Buffer Type: {self.buffer_type}, Start Index : {self.buffer_start}, Length: {self.length}' 
            
class PieceTable: 
    class BUFFER(Enum): 
        ORIGINAL = auto()
        UPDATED = auto()

        def __str__(self):
            return self.name 
        
    def __init__(self, file_data = ""):
        first_entry = Piece(self.BUFFER.ORIGINAL, 0, len(file_data)) 
        self._table = [ (first_entry) ] 
        self._original_buffer = file_data
        self._added_buffer = "" 
        self._sequence_length = len(file_data)

        self._undo_stack = [] 
        self._redo_stack = [] 
    
    def __str__(self): 
        res = ""
        for piece in self._table: 
            res += f'{piece} \n'
        return res 

    def get_table(self): 
        return self._table
    
    def get_sequence_length(self): 
        return self._sequence_length
    
    def get_original_buffer(self): 
        return self._original_buffer
    
    def get_added_buffer(self): 
        return self._added_buffer 
    
    def get_undo_stack(self): 
        return self._undo_stack 
    
    def get_redo_stack(self): 
        return self._redo_stack 
    
    def get_logical_offset(self, table_index):
        if table_index < 0: 
            raise ValueError(f'Index: {table_index} out of bounds.')

        difference = table_index
        for i in range(len(self._table)):
            curr_piece = self._table[i]
            if difference <= curr_piece.length: 
                logical_offset = curr_piece.buffer_start + difference 
                return (i, logical_offset, curr_piece) #return curr_piece as part of the tuple here 
            difference -= curr_piece.length         
        
        #TODO: throw error here 
        
    def update_table(self, start, num_updates, updates): 
        updates = list(filter(lambda piece: piece.length > 0, updates)) 
        return self._table[ : start] + updates + self._table[start + num_updates :]

    def get_sequence(self): 
        sequence = "" 
        for piece in self._table: 
            curr_buffer = self.get_buffer(piece)
            sequence += curr_buffer[piece.buffer_start : piece.buffer_start + piece.length]
        return sequence

    def get_buffer(self, piece): 
        curr_buffer = self._original_buffer if piece.buffer_type==self.BUFFER.ORIGINAL else self._added_buffer
        return curr_buffer

    def get_subsequence(self, start_index, length): 
        end_index = start_index + length 
        start_table_index, start_logical_offset, start_piece = self.get_logical_offset(start_index)
        end_table_index, end_logical_offset, end_piece = self.get_logical_offset(end_index)

        curr_buffer = self.get_buffer(start_piece)
        
        if start_table_index == end_table_index: 
            return curr_buffer[start_logical_offset : start_logical_offset + length]
        
        subsequence = curr_buffer[start_logical_offset : start_piece.buffer_start + start_piece.length]
        for i in range(start_table_index + 1, end_table_index + 1):
            curr_piece = self._table[i]
            curr_buffer = self.get_buffer(curr_piece)
            if i == end_table_index: 
                subsequence += curr_buffer[curr_piece.buffer_start : end_logical_offset]
            else: 
                subsequence += curr_buffer[curr_piece.buffer_start : curr_piece.buffer_start + curr_piece.length]
        return subsequence
    
    def reset_redo_stack(self): 
        self._redo_stack = [] 
    
    def insert(self, index, addition, reset_redo_stack = False):
        #todo: check if index > len (sequence)
        if index < 0: 
            print("ERR") #TODO: index==0
            return 

        #todo: handle misspellings here by splitting text and checking each word for a misspelling 
        if not reset_redo_stack: 
            self.reset_redo_stack() 

        added_buffer_len = len(self._added_buffer)
        self._sequence_length += len(addition)
        self._added_buffer += addition 

        table_index, logical_offset, curr_piece = self.get_logical_offset(index)

        if self._table[table_index].buffer_type == self.BUFFER.UPDATED: #todo: make sure return statement is in the correct nested conditional
            if logical_offset == self._table[table_index].buffer_start + self._table[table_index].length == added_buffer_len: #double check if triple == is needed
                self._table[table_index].length += len(addition)
                return 
        
        curr_piece = self._table[table_index]
        partition_index = logical_offset - curr_piece.buffer_start
        table_additions = [
            Piece(curr_piece.buffer_type, curr_piece.buffer_start, partition_index), 
            Piece(self.BUFFER.UPDATED, added_buffer_len, len(addition)), 
            Piece(curr_piece.buffer_type, logical_offset, curr_piece.length - partition_index), 
        ]

        self._table = self.update_table(table_index, 1, table_additions)
        self._undo_stack.append( ("INSERT", addition, index) )
        
    def delete(self, start_index, length, reset_redo_stack = False): 
        if start_index + length < 0 or start_index + length > self.get_sequence_length(): 
            raise ValueError(f'Index: {start_index + length} out of bounds for {self.get_sequence_length()}')

        if not reset_redo_stack: 
            self.reset_redo_stack() 

        start_table_index, start_logical_offset, start_piece = self.get_logical_offset(start_index)
        end_table_index, end_logical_offset, end_piece = self.get_logical_offset(start_index + length)
        self._sequence_length -= length 
        deleted_text = self.get_subsequence(start_index, length) 
        self._undo_stack.append( ("DELETE", deleted_text, start_index) ) 
        
        if start_table_index == end_table_index: 
            curr_piece = self._table[start_table_index]

            if start_logical_offset == curr_piece.buffer_start:
                curr_piece.length -= length
                curr_piece.buffer_start += length
                return 
            elif end_logical_offset == curr_piece.buffer_start + curr_piece.length: 
                curr_piece.length -= length
                return 

        table_deletions = [
            Piece(start_piece.buffer_type, start_piece.buffer_start, start_logical_offset - start_piece.buffer_start),
            Piece(end_piece.buffer_type, end_logical_offset, end_piece.length - (end_logical_offset - end_piece.buffer_start)),
        ]

        self._table = self.update_table(start_table_index, end_table_index - start_table_index + 1, table_deletions)
        
        #todo handle misspellings here again 
        
    def undo(self):
        if len(self._undo_stack) == 0: 
            print("At initial state.")
            return 
        action_type, modification_str, modification_index = self._undo_stack.pop() 
        if action_type == 'DELETE': #use an enum for this
            self.insert(modification_index, modification_str, True)
        else: 
            self.delete(modification_index, len(modification_str), True)
        self._undo_stack.pop() 
        self._redo_stack.append( (action_type, modification_str, modification_index) )
    
    def redo(self): 
        if len(self._redo_stack) == 0: 
            print("At latest state.")
            return 
        
        action_type, modification_str, modification_index = self._redo_stack.pop()
        if action_type == 'DELETE':
            self.delete(modification_index, len(modification_str), True)
        else: 
            self.insert(modification_index, modification_str, True)
from pieceTable import PieceTable 


p = PieceTable("aaabbbcccddd") 

p.insert(0, "eee")
p.insert(12, "fff")
res = p.get_sequence() 

print(f'Answer: {res}') 

p.undo()
print(p.get_sequence()) 

p.undo()
print(p.get_sequence()) 


p.undo()
print(p.get_sequence()) 
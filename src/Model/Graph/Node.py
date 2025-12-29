from threading import Lock,Condition

class Node:
    def __init__(self, node_id:int, xPos:float, yPos:float):
        self.node_id = node_id
        self.xPos = xPos
        self.yPos = yPos
        self.l = Lock()
    

    def get_position(self):
        with self.l:
            return self.xPos, self.yPos

    def get_id(self):
        with self.l:
            return self.node_id
        
    def __str__(self):
        with self.l:
            return f"{self.node_id} -|- {self.xPos}, {self.yPos}"

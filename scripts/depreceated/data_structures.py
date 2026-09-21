class Queue:

    def __init__(self, max_size: int):
        self.queue = [None] * max_size
        self.front = 0
        self.rear = 0
        self.size = 0
        self.max_size = max_size

    
    def enqueue(self, item):
        """Queues an item

        Args:
            item (Any): Item to be queued

        Raises:
            Exception: If queue is full
        """        

        if self.is_full():
            print("Warning: Queue full")
            raise Exception

        self.queue[self.rear] = item
        self.rear += 1
        self.size += 1

        self.rear %= self.max_size


    def dequeue(self):
        """Dequeues and returns the front item

        Raises:
            Exception: If queue is empty

        Returns:
            Any: Item at the front of the queue
        """        

        if self.is_empty():
            print("Warning: Queue empty")
            raise Exception
        
        item = self.queue[self.front]
        self.front += 1
        self.size -= 1

        self.front %= self.max_size
        return item

    def is_empty(self):
        return self.size == 0
    
    def is_full(self):
        return self.size == self.max_size

    def __repr__(self):
        if self.rear <= self.front:
            return str(self.queue[self.front:] + self.queue[:self.rear])

        return str(self.queue[self.front:self.rear])


class Stack:
    def __init__(self):
        self.items = [] # This makes a dynamic stack. How would you make a static stack?

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if self.isEmpty():
            print("Stack is empty")
            return None
        return self.items.pop() # Python command removes last item from a list and returns it.

    def isEmpty(self):
        return len(self.items) == 0

    def peek(self):
        if self.isEmpty():
            print("Stack is empty")
            return None
        return self.items[-1] #Python allows you to look at the last item in the list using [-1]

    def printStack(self):
        print(self.items)
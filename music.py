class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def append(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        if not self.current:
            self.current = self.head

    def get_next_song(self):
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current.data
        return None

    def get_previous_song(self):
        current = self.head
        prev = None
        while current:
            if current == self.current:
                self.current = prev
                return prev.data if prev else None
            prev = current
            current = current.next
        return None

    def remove(self, song):
        prev = None
        current = self.head
        while current:
            print(current.data)
            if current.data == song:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                if current == self.tail:
                    self.tail = prev
                return True
            prev = current
            current = current.next
        return False

    def list_all(self):
        songs = []
        current = self.head
        while current:
            songs.append(current.data)
            current = current.next
        return songs

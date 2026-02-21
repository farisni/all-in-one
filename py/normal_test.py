class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def insert_listNode(head, val):
    cur = head
    for v in arr:
        cur.next = ListNode(v)
        cur = cur.next
    return head.next


def del_listNode(head, num):
    dummy = ListNode(-1) 
    curr = head
    prev = dummy
    while curr:
        if curr.val == num:
            prev.next = curr.next # 
        else:
            prev.next = curr
        # prev = prev.next
        prev = curr
        curr = curr.next
    return dummy.next

def loop_listNode(head):
    cur = head
    while cur:
        print(cur.val, end=" -> ")
        cur = cur.next

def booabotSort():
    arr = [6,5,4,3,2,1]
    for t in range(len(arr)):
        for i in range(len(arr)-1-t) :
            if (arr[i]>arr[i+1]):
                arr[i], arr[i+1] = arr[i+1],arr[i]
    print(arr)

if __name__ == "__main__" :
    pass

    # head = ListNode(-1)
    # for i in arr:
    #     head = insert_listNode(head, i)
    
    
    
     





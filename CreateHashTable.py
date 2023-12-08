# Create Hash Map class
class CreateHashMap:
    def __init__(self, initial_capacity=20):
        self.list = []
        for i in range(initial_capacity):
            self.list.append([])

    # Inserts a new item into the hash table
    # Citation: WGU code repository W-2_ChainingHashTable_zyBooks_Key-Value_CSV_Greedy.py
    def insert(self, key, item):  # does both insert and update
        # get the bucket list where this item will go.
        bucket = hash(key) % len(self.list)
        bucket_list = self.list[bucket]

        # update key if it is already in the bucket
        for kv in bucket_list:  # O(N) CPU time
            # print (key_value)
            if kv[0] == key:
                kv[1] = item
                return True

        # if not, insert the item to the end of the bucket list
        key_value = [key, item]
        bucket_list.append(key_value)
        return True

    # Lookup items in hash table
    def lookup(self, key):
        """
        Retrieves an item from the hash table based on the provided key.

        :param key: The key used for retrieval.
        :return: The item associated with the key, or None if not found.
        """
        # Calculate the bucket index using the hash of the key
        bucket = hash(key) % len(self.list)
        bucket_list = self.list[bucket]

        # Iterate through the items in the bucket
        for pair in bucket_list:
            # Check if the key matches the current pair's key
            if key == pair[0]:
                # Return the associated item if found
                return pair[1]

        # Return None if the key is not found in the hash table
        return None

    # Hash remove method - removes item from hash table
    def hash_remove(self, key):
        slot = hash(key) % len(self.list)
        destination = self.list[slot]

        # If the key is found in the hash table then remove the item
        if key in destination:
            destination.remove(key)

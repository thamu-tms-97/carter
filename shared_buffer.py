import config
from config import logger


class SharedBuffer(object):
    '''
    Shared buffer class - holds up to 4 shards with locks for synchronization
    '''

    def __init__(self, manager):
        '''
        Initialize the shared buffer with 4 slots, each with a lock
        '''
        # a shared variable to indicate when the vj has all the shards
        self.vj_has_all_shards = manager.Value('has_all_shards', False)

        # a shared buffer which is a list of (lock, sender_name, shard_id, byte_data)
        self.__buffer = manager.list()
        for i in range(config.SHARED_BUFFER_SIZE):
            lock = manager.Lock()
            # Initially, each slot is empty (None values)
            elem = (lock, None, None, None)
            self.__buffer.append(elem)

    def lock(self, i):
        '''Get the lock for buffer slot i'''
        return self.__buffer[i][0]

    def sender_name(self, i):
        '''Get the sender name from buffer slot i'''
        return self.__buffer[i][1]

    def shard_id(self, i):
        '''Get the shard ID from buffer slot i'''
        return self.__buffer[i][2]

    def byte_data(self, i):
        '''Get the byte data from buffer slot i'''
        return self.__buffer[i][3]

    def buffer(self):
        '''Get the entire buffer'''
        return self.__buffer

    def is_slot_empty(self, i):
        '''Check if buffer slot i is empty (no data)'''
        return self.__buffer[i][3] is None

    def is_slot_full(self, i):
        '''Check if buffer slot i is full (has data)'''
        return self.__buffer[i][3] is not None

    def write_to_slot(self, i, sender_name, shard_id, byte_data):
        '''
        Write data to buffer slot i
        Must be called while holding the lock for slot i
        '''
        lock = self.__buffer[i][0]
        self.__buffer[i] = (lock, sender_name, shard_id, byte_data)

    def clear_slot(self, i):
        '''
        Clear buffer slot i (make it empty)
        Must be called while holding the lock for slot i
        '''
        lock = self.__buffer[i][0]
        self.__buffer[i] = (lock, None, None, None)
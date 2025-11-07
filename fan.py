import time

import config
from config import logger
from faker import Faker

FAKE = Faker()


class Fan(object):
    '''
    Fan class - reads assigned shards from disk and sends them to shared buffer
    '''

    def __init__(self, id, shard_ids):
        '''
        Initialize a fan with an ID and list of shard IDs to process
        
        Args:
            id: Fan identifier (0-15)
            shard_ids: List of shard IDs this fan is responsible for
        '''
        self.__id = id
        self.__name = FAKE.name()
        self.__shard_ids = shard_ids
        self.__buffer = []  # Fan's local buffer (can hold up to 16 shards)

    def id(self):
        return self.__id

    def name(self):
        return self.__name

    def buffer(self):
        return self.__buffer

    def shard_ids(self):
        return self.__shard_ids

    def read_shard_from_disk(self, shard_id):
        '''
        Read a specific shard from disk
        
        Args:
            shard_id: The ID of the shard to read (0-127)
            
        Returns:
            tuple: (shard_id, byte_data)
        '''
        padded = str(shard_id).zfill(4)
        file_path = config.SHARDS_DIR + '/' + f'shard_{padded}.mp4'

        try:
            file = open(file_path, 'rb')
        except Exception as e:
            logger.error(
                f'Unable to open {file_path} exception={type(e).__name__}')
            quit(-1)

        # read the data
        byte_data = file.read()

        # close file
        file.close()

        logger.debug(f'Fan {self.__name} (ID:{self.__id}) read shard {shard_id} from disk')

        return (shard_id, byte_data)

    def load_shards_into_buffer(self):
        '''
        Load all assigned shards from disk into the fan's local buffer
        '''
        logger.info(f'Fan {self.__name} (ID:{self.__id}) loading {len(self.__shard_ids)} shards into buffer')
        
        for shard_id in self.__shard_ids:
            shard_data = self.read_shard_from_disk(shard_id)
            self.__buffer.append(shard_data)
        
        logger.info(f'Fan {self.__name} (ID:{self.__id}) loaded {len(self.__buffer)} shards into buffer')

    def send_shard_to_shared_buffer(self, shared_buffer, shard_id, byte_data):
        '''
        Send a shard to the shared buffer
        Uses a round-robin approach to find an empty slot
        Blocks until a slot becomes available
        
        Args:
            shared_buffer: The shared buffer object
            shard_id: ID of the shard to send
            byte_data: The shard's byte data
        '''
        sent = False
        slot_index = 0
        
        while not sent:
            # Try to acquire lock for this slot
            lock = shared_buffer.lock(slot_index)
            
            # Try to acquire the lock (non-blocking - pass False as positional arg for Python 3.13 compatibility)
            if lock.acquire(False):  # Changed from lock.acquire(block=False)
                try:
                    # Check if slot is empty
                    if shared_buffer.is_slot_empty(slot_index):
                        # Write shard to this slot
                        shared_buffer.write_to_slot(slot_index, self.__name, shard_id, byte_data)
                        logger.info(f'Fan {self.__name} (ID:{self.__id}) wrote shard {shard_id} to shared buffer slot {slot_index}')
                        sent = True
                    # If slot is full, release lock and try next slot
                finally:
                    # Always release the lock
                    lock.release()
            
            if not sent:
                # Move to next slot (round-robin)
                slot_index = (slot_index + 1) % config.SHARED_BUFFER_SIZE
                # Small delay to avoid busy-waiting
                time.sleep(0.001)

    def send_all_shards(self, shared_buffer):
        '''
        Send all shards from the fan's buffer to the shared buffer
        
        Args:
            shared_buffer: The shared buffer object
        '''
        logger.info(f'Fan {self.__name} (ID:{self.__id}) sending {len(self.__buffer)} shards to shared buffer')
        
        for shard_id, byte_data in self.__buffer:
            self.send_shard_to_shared_buffer(shared_buffer, shard_id, byte_data)
            
            # Check if VJ has all shards (can exit early)
            if shared_buffer.vj_has_all_shards.value:
                logger.info(f'Fan {self.__name} (ID:{self.__id}) detected VJ has all shards, finishing')
                break
        
        logger.info(f'Fan {self.__name} (ID:{self.__id}) finished sending all shards')

    def start(self, shared_buffer):
        '''
        Main entry point for the fan process
        
        Args:
            shared_buffer: The shared buffer object
        '''
        logger.info(f'Fan {self.__name} (ID:{self.__id}) started with {len(self.__shard_ids)} shard(s): {self.__shard_ids}')
        
        # Step 1: Load shards from disk into fan buffer
        self.load_shards_into_buffer()
        
        # Step 2: Send all shards to shared buffer
        self.send_all_shards(shared_buffer)
        
        logger.info(f'Fan {self.__name} (ID:{self.__id}) completed!')

    def __str__(self):
        return f'Fan(id={self.__id}, name={self.__name}, shards={self.__shard_ids})'
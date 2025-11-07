import time

import config
import video
from config import logger


class VideoJockey(object):
    '''
    Video Jockey (Marshmello) class - receives shards and assembles the video
    '''

    def __init__(self):
        '''Initialize the VJ with an empty buffer for all 128 shards'''
        self.__name = 'Marshmello'
        # Buffer to hold all 128 shards in order
        self.__shards = [None] * config.NUM_SHARDS
        self.__shards_received = 0

    def name(self):
        return self.__name

    def shards(self):
        return self.__shards

    def shards_received(self):
        return self.__shards_received

    def has_all_shards(self):
        '''Check if VJ has received all shards'''
        return self.__shards_received >= config.NUM_SHARDS

    def __read_shard_from_shared_buffer(self, shared_buffer):
        '''
        Read a shard from the shared buffer
        Tries all 4 slots in round-robin fashion
        Blocks until a shard is available
        
        Args:
            shared_buffer: The shared buffer object
            
        Returns:
            tuple: (shard_id, byte_data, sender_name) or None if VJ has all shards
        '''
        slot_index = 0
        
        while not self.has_all_shards():
            # Try to acquire lock for this slot
            lock = shared_buffer.lock(slot_index)
            
            # Try to acquire the lock (non-blocking - pass False as positional arg for Python 3.13 compatibility)
            if lock.acquire(False):  # Changed from lock.acquire(block=False)
                try:
                    # Check if slot has data
                    if shared_buffer.is_slot_full(slot_index):
                        # Read the data
                        sender_name = shared_buffer.sender_name(slot_index)
                        shard_id = shared_buffer.shard_id(slot_index)
                        byte_data = shared_buffer.byte_data(slot_index)
                        
                        # Clear the slot (make it empty for fans to use)
                        shared_buffer.clear_slot(slot_index)
                        
                        logger.debug(f'{self.__name} read shard {shard_id} from shared buffer slot {slot_index} (from {sender_name})')
                        
                        return (shard_id, byte_data, sender_name)
                finally:
                    # Always release the lock
                    lock.release()
            
            # Move to next slot (round-robin)
            slot_index = (slot_index + 1) % config.SHARED_BUFFER_SIZE
            
            # Small delay to avoid busy-waiting
            time.sleep(0.001)
        
        return None

    def __read_all_shards(self, shared_buffer):
        '''
        Read all shards from shared buffer and store them in order
        
        Args:
            shared_buffer: The shared buffer object
            
        Returns:
            bool: True if all shards received successfully
        '''
        logger.info(f'{self.__name} starting to receive shards from shared buffer')
        
        while not self.has_all_shards():
            # Read a shard from shared buffer
            result = self.__read_shard_from_shared_buffer(shared_buffer)
            
            if result is None:
                break
            
            shard_id, byte_data, sender_name = result
            
            # Store shard in the correct position
            if self.__shards[shard_id] is None:
                self.__shards[shard_id] = byte_data
                self.__shards_received += 1
                
                # Log progress periodically
                if self.__shards_received % 16 == 0 or self.__shards_received == config.NUM_SHARDS:
                    logger.info(f'{self.__name} received shard {shard_id} from {sender_name}. Progress: {self.__shards_received}/{config.NUM_SHARDS} shards')
            else:
                logger.warning(f'{self.__name} received duplicate shard {shard_id} from {sender_name}')
        
        # Signal to all fans that VJ has all shards
        shared_buffer.vj_has_all_shards.value = True
        
        logger.info(f'{self.__name} has received all {config.NUM_SHARDS} shards!')
        return True

    def __write_video(self):
        '''
        Write all shards to disk as individual video files, then concatenate them
        
        Returns:
            str: Path to the concatenated video file
        '''
        logger.info(f'{self.__name} writing shards to disk')
        
        # Write all the shards to disk
        all_temp_file_paths = []
        for i in range(len(self.__shards)):
            if self.__shards[i] is None:
                logger.error(f'ERROR: Shard {i} is missing!')
                return None
            
            shard_data = self.__shards[i]
            video_file_path = video.write(f'shard_{i}', shard_data)
            all_temp_file_paths.append(video_file_path)
            
            # Log progress
            if (i + 1) % 32 == 0 or i == len(self.__shards) - 1:
                logger.info(f'{self.__name} wrote {i + 1}/{len(self.__shards)} shards to disk')
        
        # Concatenate all the shards into one video
        logger.info(f'{self.__name} concatenating all shards into one video')
        output_file_path = video.concat('concat_all', *all_temp_file_paths)
        
        return output_file_path

    def start(self, shared_buffer):
        '''
        Main entry point for the VJ process
        
        Args:
            shared_buffer: The shared buffer object
        '''
        logger.info(f'*** {self.__name} (VJ) started ***')
        
        # Step 1: Read all shards from shared buffer
        has_all_shards = self.__read_all_shards(shared_buffer)
        
        if has_all_shards:
            logger.info(f'*** SUCCESS! {self.__name} has all {config.NUM_SHARDS} shards! ***')
            
            # Step 2: Write the video to disk
            logger.info(f'{self.__name} writing the video')
            video_file_path = self.__write_video()
            
            if video_file_path is None:
                logger.error('ERROR: Failed to write video (missing shards)')
                return
            
            # Step 3: Add audio to the video
            logger.info(f'{self.__name} adding audio to the video')
            video_with_audio = video.audio(
                'video_with_audio',
                video_file_path,
                config.SOURCE_AUDIO_FILE_PATH
            )
            
            # Step 4: Play the video
            logger.info(f'{self.__name} playing the video on the Las Vegas Sphere!')
            logger.info(f'🎵 Now playing: "Easiest Goodbye" by Carter Skyers 🎵')
            video.play(video_with_audio)
            
            logger.info(f'*** {self.__name} completed successfully! ***')
        else:
            logger.error(f'ERROR: {self.__name} failed to receive all shards')

    def __str__(self):
        return f'VideoJockey(name={self.__name}, shards_received={self.__shards_received}/{config.NUM_SHARDS})'
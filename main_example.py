import multiprocessing
import time

import config
import fan
import shared_buffer as sb
import video
import video_jockey
from config import logger


def distribute_shards_to_fans(num_shards, num_fans):
    '''
    Distribute shards evenly among fans
    
    Args:
        num_shards: Total number of shards (128)
        num_fans: Number of fan processes (16)
        
    Returns:
        list: List of lists, where each sublist contains shard IDs for a fan
              Example: [[0,1,2,3,4,5,6,7], [8,9,10,...], ...]
    '''
    shards_per_fan = num_shards // num_fans  # 128 // 16 = 8
    remainder = num_shards % num_fans  # 128 % 16 = 0
    
    fan_shard_assignments = []
    shard_id = 0
    
    for fan_id in range(num_fans):
        # Calculate how many shards this fan gets
        # If there's a remainder, give extra shards to first few fans
        num_shards_for_this_fan = shards_per_fan + (1 if fan_id < remainder else 0)
        
        # Assign shard IDs to this fan
        shard_list = list(range(shard_id, shard_id + num_shards_for_this_fan))
        fan_shard_assignments.append(shard_list)
        
        shard_id += num_shards_for_this_fan
    
    return fan_shard_assignments


def main():
    
    # Main function - orchestrates the entire video streaming system
    
    logger.info('=' * 80)
    logger.info('CARTER SKYERS - EASIEST GOODBYE - VIDEO STREAMING TO LAS VEGAS SPHERE')
    logger.info('=' * 80)
    logger.info(f'Configuration:')
    logger.info(f'  - Total shards: {config.NUM_SHARDS}')
    logger.info(f'  - Fan processes: {config.NUM_FANS}')
    logger.info(f'  - Shared buffer size: {config.SHARED_BUFFER_SIZE}')
    logger.info(f'  - Fan buffer size: {config.FAN_BUFFER_SIZE}')
    logger.info('=' * 80)

    # Clean any temp files from previous runs
    logger.info('Cleaning temporary directory...')
    video.clean_temp_directory()

    # Create a manager to share data between processes
    manager = multiprocessing.Manager()

    # Create the shared buffer (4 slots with locks)
    shared_buffer = sb.SharedBuffer(manager)
    logger.info('Shared buffer created')

    # Distribute shards among fans
    fan_shard_assignments = distribute_shards_to_fans(config.NUM_SHARDS, config.NUM_FANS)
    
    logger.info('\nShard distribution:')
    for i, shard_list in enumerate(fan_shard_assignments):
        logger.info(f'  Fan {i}: {len(shard_list)} shards (IDs {min(shard_list)}-{max(shard_list)})')
    logger.info('')

    # Create the VJ (Marshmello) process
    vj = video_jockey.VideoJockey()
    vj_process = multiprocessing.Process(
        target=vj.start,
        args=([shared_buffer]),
        name='Marshmello-VJ'
    )
    
    # Create all fan processes
    fan_processes = []
    for i in range(config.NUM_FANS):
        # Create a fan with its assigned shard IDs
        f = fan.Fan(i, fan_shard_assignments[i])
        
        # Create a process for this fan
        fan_process = multiprocessing.Process(
            target=f.start,
            args=([shared_buffer]),
            name=f'Fan-{i}'
        )
        
        fan_processes.append(fan_process)

    # Start timing
    start_time = time.time()
    
    # Start the VJ process first (so it's ready to receive)
    logger.info(f'Starting VJ process: {vj.name()}')
    vj_process.start()
    
    # Small delay to ensure VJ is ready
    time.sleep(0.1)
    
    # Start all fan processes
    logger.info(f'Starting {len(fan_processes)} fan processes...')
    for i, fan_proc in enumerate(fan_processes):
        fan_proc.start()
        logger.debug(f'Started Fan-{i}')
    
    logger.info('All processes started!')
    logger.info('=' * 80)

    # Wait for all fan processes to complete
    logger.info('Waiting for fan processes to complete...')
    for i, fan_proc in enumerate(fan_processes):
        fan_proc.join()
        logger.debug(f'Fan-{i} completed')
    
    logger.info('All fan processes completed!')

    # Wait for VJ process to complete
    logger.info('Waiting for VJ process to complete...')
    vj_process.join()
    logger.info('VJ process completed!')

    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    logger.info('=' * 80)
    logger.info(f'*** ALL PROCESSES COMPLETED SUCCESSFULLY! ***')
    logger.info(f'*** Total time: {elapsed_time:.2f} seconds ***')
    logger.info('=' * 80)


# Main should only execute for the main process
if __name__ == '__main__':
    main()
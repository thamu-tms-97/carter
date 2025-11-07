import logging
import os

# project directory
PROJECT_DIR = r'C:\Users\thmrt\Downloads\carter'

# number of shards in the video
NUM_SHARDS = 128

# number of fan processes to spawn
NUM_FANS = 8

# get logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Change to DEBUG for more detailed output

# buffer parameters
FAN_BUFFER_SIZE = 16
SHARED_BUFFER_SIZE = 4

# temporary directory for videos
TEMP_DIR = os.path.join(PROJECT_DIR, 'temp')

# url
URL = 'https://www.youtube.com/watch?v=WU4UxWaf8U8&list=PLIx-eqjsmIuCoHbep0iithAFB6U793VVA'

# source hires files
SOURCE_VIDEO_BASENAME = 'carter-skyers-easiest-goodbye-official-music-video'
SOURCE_VIDEO_FILE_PATH = os.path.join(PROJECT_DIR, 'video', SOURCE_VIDEO_BASENAME + '.mp4')
SOURCE_AUDIO_FILE_PATH = os.path.join(PROJECT_DIR, 'video', SOURCE_VIDEO_BASENAME + '.mp3')

# video epsilon
TIME_EPSILON = 0.0000001

# shards json file
SHARDS_DIR = os.path.join(PROJECT_DIR, 'video_shards')
SHARDS_JSON_FILE_PATH = os.path.join(SHARDS_DIR, 'shards.json')

# Simplified logging format for consistent instructor output
FORMAT = '[%(levelname)-8s] %(message)s'
logging.basicConfig(format=FORMAT)

# test short video files
TEST_VIDEO_BASENAME = 'carter-skyers-easiest-goodbye-official-music-video'
TEST_VIDEO_FILE_PATH = os.path.join(PROJECT_DIR, 'video_test', TEST_VIDEO_BASENAME + '.mp4')
TEST_AUDIO_FILE_PATH = os.path.join(PROJECT_DIR, 'video_test', TEST_VIDEO_BASENAME + '.mp3')
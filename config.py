import logging

#
# STUDENTS NEED TO CHANGE THE PROJECT DIRECTORY FOR THEIR COMPUTER
#
# project directory
PROJECT_DIR = '/Users/jerom/Documents/GitHub/class-python/carter-skyers-video-stream/example'

#
# STUDENTS MAY WISH TO CHANGE (REDUCE) THE FOLLOWING PARAMETERS WHILE TESTING AND DEBUGGING THEIR CODE
#
# number of shards in the video
NUM_SHARDS = 128

# number of fan processes to spawn
NUM_FANS = 16

#
# STUDENTS MAY WISH TO CHANGE THE LOGGING LEVEL WHILE TESTING AND DEBUGGING THEIR CODE
#
# get logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#
# STUDENTS CAN, BUT SHOULD NOT NEED TO CHANGE ANYTHING BELOW THIS LINE
#

# buffer parameters
FAN_BUFFER_SIZE = 16
SHARED_BUFFER_SIZE = 4

# temporary directory for videos
TEMP_DIR = PROJECT_DIR + '/temp'

# url
URL = 'https://www.youtube.com/watch?v=WU4UxWaf8U8&list=PLIx-eqjsmIuCoHbep0iithAFB6U793VVA'

# source hires files
SOURCE_VIDEO_BASENAME = 'carter-skyers-easiest-goodbye-official-music-video'
SOURCE_VIDEO_FILE_PATH = PROJECT_DIR + '/video/' + SOURCE_VIDEO_BASENAME + '.mp4'
SOURCE_AUDIO_FILE_PATH = PROJECT_DIR + '/video/' + SOURCE_VIDEO_BASENAME + '.mp3'

# video epsilon
TIME_EPSILON = 0.0000001

# shards json file
SHARDS_DIR = PROJECT_DIR + '/video_shards'
SHARDS_JSON_FILE_PATH = SHARDS_DIR + '/shards.json'

# configure log output format
FORMAT = '[%(asctime)s:%(levelname)-8s] %(message)s'
logging.basicConfig(format=FORMAT)


# test short video files
TEST_VIDEO_BASENAME = 'carter-skyers-easiest-goodbye-official-music-video'
TEST_VIDEO_FILE_PATH = PROJECT_DIR + '/video_test/' + TEST_VIDEO_BASENAME + '.mp4'
TEST_AUDIO_FILE_PATH = PROJECT_DIR + '/video_test/' + TEST_VIDEO_BASENAME + '.mp3'

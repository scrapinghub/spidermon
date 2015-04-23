#-----------------------------------------------------
# Levels
#-----------------------------------------------------
LEVEL_HIGH = 'HIGH'
LEVEL_NORMAL = 'NORMAL'
LEVEL_LOW = 'LOW'
LEVELS = (
    LEVEL_HIGH,
    LEVEL_NORMAL,
    LEVEL_LOW,
)
DEFAULT_LEVEL = LEVEL_NORMAL

#-----------------------------------------------------
# Check states
#-----------------------------------------------------
CHECK_STATE_PASSED = 'PASSED'
CHECK_STATE_FAILED = 'FAILED'
CHECK_STATE_ERROR = 'ERROR'
CHECK_STATE_ALWAYS = 'ALWAYS'
CHECK_STATES = (
    CHECK_STATE_PASSED,
    CHECK_STATE_FAILED,
    CHECK_STATE_ERROR,
)
DEFAULT_CHECK_STATE = CHECK_STATE_ALWAYS

#-----------------------------------------------------
# Action states
#-----------------------------------------------------
ACTION_STATE_PROCESSED = 'PROCESSED'
ACTION_STATE_SKIPPED = 'SKIPPED'
ACTION_STATE_ERROR = 'ERROR'
ACTION_STATES = (
    ACTION_STATE_PROCESSED,
    ACTION_STATE_SKIPPED,
    ACTION_STATE_ERROR,
)

#-----------------------------------------------------
# Action triggers
#-----------------------------------------------------
ACTION_TRIGGERS = (
    CHECK_STATE_PASSED,
    CHECK_STATE_FAILED,
    CHECK_STATE_ERROR,
    CHECK_STATE_ALWAYS,
)

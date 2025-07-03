from core.summaries.prompts import SYSTEM_MESSAGE_SUMMARY_STEP_1, SYSTEM_MESSAGE_SUMMARY_STEP_2, SYSTEM_MESSAGE_POSITIVE_TAGS, SYSTEM_MESSAGE_NEGATIVE_TAGS, SYSTEM_MESSAGE_TAGS

MIN_SOURCES_FOR_SUMMARY = 3

SUMMARY_CONFIG = {
    'step_1': {
        'model': 'gpt-4.1-mini',
        'system_message': SYSTEM_MESSAGE_SUMMARY_STEP_1
    },
    'step_2': {
        'model': 'gpt-4.1',
        'system_message': SYSTEM_MESSAGE_SUMMARY_STEP_2
    },
    'positive_tags': {
        'model': 'gpt-4.1',
        'system_message': SYSTEM_MESSAGE_POSITIVE_TAGS
    },
    'negative_tags': {
        'model': 'gpt-4.1',
        'system_message': SYSTEM_MESSAGE_NEGATIVE_TAGS
    },
    'tags': {
        'model': 'gpt-4.1-mini',
        'system_message': SYSTEM_MESSAGE_TAGS
    }
}

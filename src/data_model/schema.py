COMMENT_COLUMNS = [
    "post_id",
    "post_type",
    "post_link",
    "comment_id",
    "comment_text",
    "manual_label",
    "model_label",
    "note",
]

POST_CONTEXT_COLUMNS = [
    "post_id",
    "post_type",
    "post_text",
    "image_context_text",
    "video_context_text",
    "note",
]

SENTIMENT_CONTEXT_COLUMNS = [
    "post_sentiment_label",
    "post_sentiment_confidence",
    "post_original_model_label",

    "image_context_sentiment_label",
    "image_context_sentiment_confidence",
    "image_context_original_model_label",

    "video_context_sentiment_label",
    "video_context_sentiment_confidence",
    "video_context_original_model_label",
]

INTERNAL_DATA_COLUMNS = [
    "post_id",
    "post_type",
    "post_link",

    "post_text",
    "image_context_text",
    "video_context_text",

    "comment_id",
    "comment_text",
    "manual_label",

    "model_label",
    "confidence",
    "original_model_label",

    "post_sentiment_label",
    "post_sentiment_confidence",
    "post_original_model_label",

    "image_context_sentiment_label",
    "image_context_sentiment_confidence",
    "image_context_original_model_label",

    "video_context_sentiment_label",
    "video_context_sentiment_confidence",
    "video_context_original_model_label",

    "note",
]

REQUIRED_COMMENT_COLUMNS = [
    "post_id",
    "comment_id",
    "comment_text",
]

REQUIRED_POST_CONTEXT_COLUMNS = [
    "post_id",
    "post_type",
    "post_text",
]
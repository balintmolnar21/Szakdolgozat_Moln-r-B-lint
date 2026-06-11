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
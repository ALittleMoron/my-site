from settings.config import config

MARTOR_THEME = "semantic"
MARTOR_ENABLE_CONFIGS = {
    "emoji": "true",
    "imgur": "true",
    "mention": "false",
    "jquery": "true",
    "living": "false",
    "spellcheck": "false",
    "hljs": "true",
}
MARTOR_TOOLBAR_BUTTONS = [
    "bold",
    "italic",
    "horizontal",
    "heading",
    "pre-code",
    "blockquote",
    "unordered-list",
    "ordered-list",
    "link",
    "image-link",
    "image-upload",
    "emoji",
    "direct-mention",
    "toggle-maximize",
    "help",
]
MARTOR_ENABLE_LABEL = config.martor.enable_label
MARTOR_ENABLE_ADMIN_CSS = config.martor.enable_admin_css
MARTOR_MARKDOWNIFY_TIMEOUT = config.martor.markdownify_timeout
MARTOR_UPLOAD_PATH = config.martor.upload_path
MARTOR_UPLOAD_URL = config.martor.upload_url
MAX_IMAGE_UPLOAD_SIZE = config.martor.max_image_upload_size
MDEDITOR_CONFIGS = {
    "default": {
        "width": "90% ",
        "height": 500,
        "toolbar": [
            "undo",
            "redo",
            "|",
            "bold",
            "del",
            "italic",
            "quote",
            "ucwords",
            "uppercase",
            "lowercase",
            "|",
            "h1",
            "h2",
            "h3",
            "h5",
            "h6",
            "|",
            "list-ul",
            "list-ol",
            "hr",
            "|",
            "link",
            "reference-link",
            "image",
            "code",
            "preformatted-text",
            "code-block",
            "table",
            "datetime",
            "emoji",
            "html-entities",
            "pagebreak",
            "goto-line",
            "|",
            "preview",
            "watch",
            "fullscreen",
            "||",
            "help",
        ],  # custom edit box toolbar
        "upload_image_formats": [
            "jpg",
            "jpeg",
            "gif",
            "png",
            "bmp",
            "webp",
        ],  # image upload format type
        "upload_image_url": "/markdown-upload-image/",
        "theme": "default",
        "preview_theme": "default",
        "editor_theme": "default",
        "toolbar_autofixed": True,
        "search_replace": True,
        "emoji": True,
        "tex": True,
        "flow_chart": True,
        "sequence": True,
        "watch": True,
        "lineWrapping": True,
        "lineNumbers": True,
        "language": "ru",
    },
}

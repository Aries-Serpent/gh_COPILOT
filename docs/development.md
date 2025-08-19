# Development Guide

## Web GUI Debug Mode

The Web GUI reads the ``WEB_GUI_DEBUG`` environment variable to determine
whether to enable Flask's debug features. In ``web_gui/config.py``,
``DEBUG`` defaults to ``False`` so sensitive information is not exposed.
To enable debug output while developing, set the variable to ``1``:

```bash
export WEB_GUI_DEBUG=1
```

Avoid using this setting in production deployments.

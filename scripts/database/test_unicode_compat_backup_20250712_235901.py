#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unicode compatibility test file"""


def test_unicode_handling():
    """Test Unicode string handling"""
    message = "Unicode test: áéíóú, 中文, Русский"
    return message


if __name__ == "__main__":
    print(test_unicode_handling())

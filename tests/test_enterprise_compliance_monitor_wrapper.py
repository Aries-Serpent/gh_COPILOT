#!/usr/bin/env python3
import scripts.monitoring.enterprise_compliance_monitor as wrapper


def test_wrapper_exposes_main():
    assert callable(wrapper.enterprise_main)

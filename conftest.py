import sys

collect_ignore = []
if sys.version_info.major < 3:
    collect_ignore.append("tests/test_py3_annotation.py")
    collect_ignore.append("tests/test_py3_constraint.py")
    collect_ignore.append("tests/test_py3_types.py")
    collect_ignore.append("tests/test_py3_usage.py")

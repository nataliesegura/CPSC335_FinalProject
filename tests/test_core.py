"""Public tests (pytest version of check_project.py).   Run:  python -m pytest -q"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import check_project as C  # noqa: E402


def test_part1_build_index(): C.part1()
def test_part2_sort_and_search(): C.part2()
def test_part3_min_heap(): C.part3()
def test_part4_greedy(): C.part4()
def test_part5_dp(): C.part5()
def test_part6_graphs(): C.part6()
def test_part7_kmp(): C.part7()
def test_part8_tour(): C.part8()
def test_rules_no_builtin_shortcuts(): assert C.rules() == []

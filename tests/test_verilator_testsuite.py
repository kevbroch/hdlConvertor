# import sys
import os
import unittest

from hdlConvertor import HdlConvertor
from hdlConvertor.language import Language
from tests.time_logging_test_runner import TimeLoggingTestRunner
from tests.file_utils import find_files, TestFilter, generate_test_method_name, \
    get_file_name
import re

VERILATOR_TEST_ROOT = os.path.join(os.path.dirname(__file__),
                                   "verilator", "test_regress", "t")

# use this file to run tests in incremental maner,
# the test which passed in previous build will not be executed again
SUCESSFULL_TEST_FILTER_FILE = "tests_passed.verilator"
# SUCESSFULL_TEST_FILTER_FILE = None


def get_verilator_test_config():
    RE_TOPFILENAME = re.compile('top_filename\("\s*([^"]+)"\s*\)', re.MULTILINE)
    for test_script_name in find_files(VERILATOR_TEST_ROOT, "*.pl"):
        do_ignore = False
        for ignored in ["t_flag_", "t_dist_", "t_vlcov_",
                        "t_verilated_all_oldest.pl", "bootstrap.pl",
                        "t_driver_random.pl",
                        "t_debug_",
                        ]:
            if ignored in test_script_name:
                do_ignore = True
                break
        if do_ignore:
            continue
        with open(test_script_name) as f:
            s = f.read()
        should_fail = "fails => 1" in s
        main_file = RE_TOPFILENAME.search(s)
        if main_file is not None:
            main_file = main_file.group(1)
            if "$Self->{obj_dir}" in main_file:
                continue
            assert main_file.startswith("t/") or main_file.startswith("t_"), main_file
            main_file = os.path.basename(main_file)
        else:
            verilog_file = test_script_name.replace(".pl", ".v")
            if os.path.exists(verilog_file):
                main_file = os.path.basename(verilog_file)
            else:
                verilog_file = test_script_name.replace(".pl", ".sv")
                if os.path.exists(verilog_file):
                    main_file = os.path.basename(verilog_file)
                else:
                    raise NotImplementedError(test_script_name)

        yield os.path.join(VERILATOR_TEST_ROOT, main_file), should_fail


# https://stackoverflow.com/questions/32899/how-do-you-generate-dynamic-parameterized-unit-tests-in-python
class VerilatorTestsuiteMeta(type):

    def __new__(cls, name, bases, _dict):
        test_filter = TestFilter(SUCESSFULL_TEST_FILTER_FILE)

        def gen_test(sv_file, should_fail, verilog_version):

            def test(self):
                debug = False
                c = HdlConvertor()
                incdirs = [VERILATOR_TEST_ROOT, ]

                try:
                    c.parse([sv_file, ], verilog_version, incdirs, debug=debug)
                except Exception:
                    if should_fail:
                        # [TODO] some expected erros in this test suite are not related to synatax
                        #        need to check maually if the error really means syntax error and
                        #        if this library is raising it correctly
                        pass
                    else:
                        raise
                test_filter.mark_test_as_passed(self)

            return test

        lang = Language.SYSTEM_VERILOG_2009
        for file_name, should_fail in sorted(set(get_verilator_test_config()),
                                             key=lambda x: x[0]):
            fn = get_file_name(file_name)
            test_name = generate_test_method_name(fn, lang, _dict)

            if not test_filter.is_dissabled_test(test_name):
                _dict[test_name] = gen_test(file_name, should_fail, lang)

        return type.__new__(cls, name, bases, _dict)


# https://www.oipapio.com/question-219175 , python2/3 compatible specification of metatype for class
VerilatorTestsuiteTC = VerilatorTestsuiteMeta('VerilatorTestsuiteTC', (unittest.TestCase,), {})

if __name__ == '__main__':
    # unittest.main(failfast=True)
    suite = unittest.TestSuite()

    # suite.addTest(VerilatorTestsuiteTC('test_SYSTEM_VERILOG_2009_t_preproc'))
    suite.addTest(unittest.makeSuite(VerilatorTestsuiteTC))

    runner = TimeLoggingTestRunner(verbosity=3)
    runner.run(suite)
# Copyright (C) 2024 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""
Test predefined events
"""
import unittest
from scenario_execution_base import ScenarioExecution
from scenario_execution_base.model.osc2_parser import OpenScenario2Parser
from scenario_execution_base.model.model_to_py_tree import create_py_tree
from scenario_execution_base.utils.logging import Logger
from antlr4.InputStream import InputStream


class TestOSC2Parser(unittest.TestCase):
    # pylint: disable=missing-function-docstring, protected-access, no-member, unused-variable

    def setUp(self) -> None:
        self.parser = OpenScenario2Parser(Logger('test'))
        self.scenario_execution = ScenarioExecution(debug=True, log_model=True, live_tree=True, scenario='test.osc', output_dir="")

    def test_failure(self):
        scenario_content = """
scenario test:
    do serial:
        emit fail
"""
        parsed_tree, errors = self.parser.parse_input_stream(InputStream(scenario_content))
        self.assertEqual(errors, 0)
        model = self.parser.create_internal_model(parsed_tree, "test.osc", True)
        self.assertIsNotNone(model)
        scenarios = create_py_tree(model, self.parser.logger)
        self.assertIsNotNone(scenarios)
        self.scenario_execution.scenarios = scenarios
        ret = self.scenario_execution.run()
        self.assertFalse(ret)

    def test_success(self):
        scenario_content = """
scenario test:
    do serial:
        emit end
"""
        parsed_tree, errors = self.parser.parse_input_stream(InputStream(scenario_content))
        self.assertEqual(errors, 0)
        model = self.parser.create_internal_model(parsed_tree, "test.osc", True)
        self.assertIsNotNone(model)
        scenarios = create_py_tree(model, self.parser.logger)
        self.assertIsNotNone(scenarios)
        self.scenario_execution.scenarios = scenarios
        ret = self.scenario_execution.run()
        self.assertTrue(ret)

    def test_wait_for_event(self):
        scenario_content = """
type time is SI(s: 1)
unit s          of time is SI(s: 1, factor: 1)

scenario test:
    event test
    do parallel:
        serial:
            wait elapsed(1s)
            emit test
            wait elapsed(10s)
            emit fail
        serial:
            wait @test
            emit end
"""
        parsed_tree, errors = self.parser.parse_input_stream(InputStream(scenario_content))
        self.assertEqual(errors, 0)
        model = self.parser.create_internal_model(parsed_tree, "test.osc", True)
        self.assertIsNotNone(model)
        scenarios = create_py_tree(model, self.parser.logger)
        self.assertIsNotNone(scenarios)
        self.scenario_execution.scenarios = scenarios
        ret = self.scenario_execution.run()
        self.assertTrue(ret)

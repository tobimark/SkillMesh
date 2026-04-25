from __future__ import annotations
import re
from typing import Any


class TemplateEngine:
    """Simple template engine for {{variable}} substitution."""

    VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")

    @classmethod
    def substitute(cls, text: str, variables: dict[str, Any]) -> str:
        """
        Replace {{variable}} patterns in text with values from variables dict.
        If a variable is not found, leave the placeholder as-is.
        """
        def replace_match(match: re.Match) -> str:
            var_name = match.group(1)
            value = variables.get(var_name)
            if value is None:
                return match.group(0)  # Keep placeholder if not found
            return str(value)

        return cls.VARIABLE_PATTERN.sub(replace_match, text)

    @classmethod
    def evaluate_condition(cls, condition: str, variables: dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.
        Currently supports: truthy values, comparisons.
        Format: '{{variable}}' or '{{variable}}' == 'value' etc.
        """
        condition = condition.strip()

        # Handle simple {{variable}} form - truthy check
        if cls.VARIABLE_PATTERN.fullmatch(condition):
            var_name = cls.VARIABLE_PATTERN.fullmatch(condition).group(1)
            value = variables.get(var_name)
            return bool(value)

        # Handle comparisons: {{a}} == 'b', {{a}} != 'b', etc.
        for op in ["==", "!=", ">", "<", ">=", "<="]:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    left = cls.substitute(parts[0].strip(), variables).strip()
                    right = cls.substitute(parts[1].strip(), variables).strip()
                    right = right.strip("'\"")

                    try:
                        left_num = float(left)
                        right_num = float(right)
                        if op == "==":
                            return left_num == right_num
                        elif op == "!=":
                            return left_num != right_num
                        elif op == ">":
                            return left_num > right_num
                        elif op == "<":
                            return left_num < right_num
                        elif op == ">=":
                            return left_num >= right_num
                        elif op == "<=":
                            return left_num <= right_num
                    except ValueError:
                        if op == "==":
                            return left == right
                        elif op == "!=":
                            return left != right

        return False
